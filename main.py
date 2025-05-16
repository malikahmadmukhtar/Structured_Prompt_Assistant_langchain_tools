import re
import uuid
import streamlit as st
from app.history.chat_history import delete_chat, get_truncated_name, save_chat, get_chat_files, load_chat, \
    add_message_to_history, get_last_n_messages
from app.utils.agent import agent_executor
from app.utils.facebook.product_creation import upload_image_to_cloudinary, finalize_product_upload
from config.settings import meta_image, agent_image, user_image, active_model

# --- STREAMLIT UI ---
st.set_page_config(page_title="Meta Assistant", page_icon=agent_image, layout="wide")

col1, col2 = st.columns([1, 5])
with col1:
    st.image(image=meta_image, output_format="PNG", width=120)
with col2:
    st.title("AI Based Meta Campaign Assistant")

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

    if col1.button(chat_title, key=f"load_{file}",use_container_width=True):
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
    col_confirm, col_cancel = st.sidebar.columns([0.5, 0.5])
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
    with st.spinner(f"{active_model} is working on it"):
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

# Image upload inside assistant chat bubble
if "pending_product" in st.session_state:
    with st.chat_message("assistant", avatar=agent_image):
        st.info("Finish product creation by uploading an image:")
        image_file = st.file_uploader("Upload Product Image", type=["jpg", "jpeg", "png"], key="product_image_upload")

        if image_file:
            try:
                image_url = upload_image_to_cloudinary(image_file)
                if not image_url:
                    st.error("❌ Failed to upload image. Please try again with a different file.")
                else:
                    try:
                        product_id = finalize_product_upload(st.session_state["pending_product"], image_url)
                        if product_id.startswith("Error"):
                            st.error(f"❌ Product creation failed: {product_id}")
                        else:
                            # st.success(f"Product created successfully with ID: `{product_id}`")
                            add_message_to_history("agent", f"Product created successfully with ID: `{product_id}`", st.session_state.chat_history)

                            del st.session_state["pending_product"]
                    except Exception as e:
                        st.error(f"❌ Unexpected error during product creation: {e}")
            except Exception as e:
                st.error(f"❌ Image upload failed due to an unexpected error: {e}")
