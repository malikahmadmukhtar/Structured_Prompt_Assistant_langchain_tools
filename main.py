import re
import uuid
import streamlit as st
from app.history.chat_history import delete_chat, get_truncated_name, save_chat, get_chat_files, load_chat, \
    add_message_to_history, get_last_n_messages
from app.utils.agent import agent_executor
from config.settings import meta_image, agent_image, user_image

# --- STREAMLIT UI ---
st.set_page_config(page_title="Meta Assistant", page_icon=agent_image, layout="wide")
# st.title("🤖 Groq Agent with Tools + History")

col1, col2 = st.columns([1,5])
with col1:
    st.image(image=meta_image, output_format="PNG", width=120)
with col2:
    st.title("AI Based Meta Campaign Assistant")

# st.header("Structured Output prototype")
st.header("Type below to get Started")

# Session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "chat_id" not in st.session_state:
    st.session_state.chat_id = str(uuid.uuid4())
if "confirm_delete" not in st.session_state:
    st.session_state.confirm_delete = None
if "loaded_file" not in st.session_state:
    st.session_state.loaded_file = None


# New Chat Button
if st.sidebar.button("➕ Start New Chat"):
    st.session_state.chat_history = []
    st.session_state.chat_id = str(uuid.uuid4())
    st.session_state.loaded_file = None
    st.rerun()

# Sidebar - Previous chats
st.sidebar.subheader("💬 Previous Chats")

chat_files = get_chat_files()

for file in chat_files:
    chat_title = get_truncated_name(file.rsplit("_", 1)[0].replace("_", " "))
    col1, col2 = st.sidebar.columns([1, 0.2])

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
    col_confirm, col_cancel = st.sidebar.columns([0.5,0.5])
    if col_confirm.button("✅ Yes"):
        delete_chat(st.session_state.confirm_delete)
        st.session_state.confirm_delete = None
        if st.session_state.loaded_file == st.session_state.confirm_delete:
            st.session_state.chat_history = []
        st.rerun()
    if col_cancel.button("❌ No"):
        st.session_state.confirm_delete = None


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
    print(f"\n\nRaw LLM reponse: {response}")
    reply = response.get("output", "")

    ## Removing reasoning tags
    cleaned_reply = re.sub(r"<think>.*?</think>", "", reply, flags=re.DOTALL).strip()

    add_message_to_history("agent", cleaned_reply, st.session_state.chat_history)

    # Save chat
    first_message = st.session_state.chat_history[0][1] if st.session_state.chat_history else "chat"
    filename_base = "_".join(first_message.strip().lower().split()[:5])
    save_chat(filename_base.replace(" ", "_"), st.session_state.chat_id, st.session_state.chat_history)

# Display messages
# Display chat messages
for role, msg in st.session_state.chat_history:
    avatar = agent_image if role == "agent" else user_image
    with st.chat_message(role, avatar=avatar):
        st.markdown(msg)

