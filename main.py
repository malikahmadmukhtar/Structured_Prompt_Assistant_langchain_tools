import uuid
import streamlit as st
from app.history.chat_history import delete_chat, get_truncated_name, save_chat, get_chat_files, load_chat, \
    add_message_to_history, get_last_n_messages
from app.utils.agent import agent_executor

# --- STREAMLIT UI ---
st.set_page_config(page_title="Groq Chat Agent", page_icon="🤖")
st.title("🤖 Groq Agent with Tools + History")

# Session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "chat_id" not in st.session_state:
    st.session_state.chat_id = str(uuid.uuid4())
if "confirm_delete" not in st.session_state:
    st.session_state.confirm_delete = None
if "loaded_file" not in st.session_state:
    st.session_state.loaded_file = None

# Sidebar - Previous chats
st.sidebar.subheader("💬 Previous Chats")

chat_files = get_chat_files()

for file in chat_files:
    chat_title = get_truncated_name(file.rsplit("_", 1)[0].replace("_", " "))
    col1, col2 = st.sidebar.columns([0.75, 0.25])

    if col1.button(chat_title, key=f"load_{file}"):
        data = load_chat(file)
        st.session_state.chat_history = data["messages"]
        st.session_state.chat_id = file.rsplit("_", 1)[-1].replace(".json", "")
        st.session_state.loaded_file = file
        st.rerun()

    if col2.button("🗑", key=f"delete_{file}"):
        st.session_state.confirm_delete = file

# Confirm deletion
if st.session_state.confirm_delete:
    st.sidebar.warning(f"Delete '{get_truncated_name(st.session_state.confirm_delete)}'?")
    col_confirm, col_cancel = st.sidebar.columns(2)
    if col_confirm.button("✅ Yes"):
        delete_chat(st.session_state.confirm_delete)
        st.session_state.confirm_delete = None
        if st.session_state.loaded_file == st.session_state.confirm_delete:
            st.session_state.chat_history = []
        st.rerun()
    if col_cancel.button("❌ No"):
        st.session_state.confirm_delete = None

# New Chat Button
if st.sidebar.button("➕ Start New Chat"):
    st.session_state.chat_history = []
    st.session_state.chat_id = str(uuid.uuid4())
    st.session_state.loaded_file = None
    st.rerun()

# Chat input
user_input = st.chat_input("Ask me something...")

if user_input:
    # Append user message
    add_message_to_history("user", user_input, st.session_state.chat_history)

    # Get the last 20 messages to pass to the LLM
    last_20_messages = get_last_n_messages(st.session_state.chat_history, 20)

    # Prepare the context for the agent
    context = "\n".join([f"{role}: {message}" for role, message in last_20_messages])

    # Agent response
    response = agent_executor.invoke({"input": context})
    reply = response.get("output", "")
    add_message_to_history("agent", reply, st.session_state.chat_history)

    # Save chat
    first_message = st.session_state.chat_history[0][1] if st.session_state.chat_history else "chat"
    filename_base = "_".join(first_message.strip().lower().split()[:5])
    save_chat(filename_base.replace(" ", "_"), st.session_state.chat_id, st.session_state.chat_history)

# Display messages
for role, msg in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(msg)
