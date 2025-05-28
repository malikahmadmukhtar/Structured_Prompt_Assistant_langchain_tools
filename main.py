# import re
# import uuid
# import streamlit as st
# from app.history.chat_history import delete_chat, get_truncated_name, save_chat, get_chat_files, load_chat, \
#     add_message_to_history, get_last_n_messages
# from app.utils.agent import agent_executor
# from app.utils.facebook.creative_creation import upload_image_to_facebook, finalize_creative_upload
# from app.utils.facebook.product_creation import upload_image_to_cloudinary, finalize_product_upload
# from config.settings import meta_image, agent_image, user_image, active_model
#
# # --- STREAMLIT UI ---
# st.set_page_config(page_title="Meta Assistant", page_icon=agent_image, layout="wide")
#
# col1, col2 = st.columns([1, 5])
# with col1:
#     st.image(image=meta_image, output_format="PNG", width=120)
# with col2:
#     st.title("AI Based Meta Campaign Assistant")
#
# st.header("Type below to get Started")
#
# # Session state
# if "chat_history" not in st.session_state:
#     st.session_state.chat_history = []
# if "chat_id" not in st.session_state:
#     st.session_state.chat_id = str(uuid.uuid4())
# if "confirm_delete" not in st.session_state:
#     st.session_state.confirm_delete = None
# if "loaded_file" not in st.session_state:
#     st.session_state.loaded_file = None
#
# # New Chat Button
# if st.sidebar.button("➕ Start New Chat"):
#     st.session_state.chat_history = []
#     st.session_state.chat_id = str(uuid.uuid4())
#     st.session_state.loaded_file = None
#     st.rerun()
#
# # Sidebar - Previous chats
# st.sidebar.subheader("💬 Previous Chats")
#
# chat_files = get_chat_files()
#
# for file in chat_files:
#     chat_title = get_truncated_name(file.rsplit("_", 1)[0].replace("_", " "))
#     col1, col2 = st.sidebar.columns([1, 0.2])
#
#     if col1.button(chat_title, key=f"load_{file}",use_container_width=True):
#         data = load_chat(file)
#         st.session_state.chat_history = data["messages"]
#         st.session_state.chat_id = file.rsplit("_", 1)[-1].replace(".json", "")
#         st.session_state.loaded_file = file
#         st.rerun()
#
#     if col2.button("🗑", key=f"delete_{file}"):
#         st.session_state.confirm_delete = file
#
# # Confirm deletion
# if st.session_state.confirm_delete:
#     st.sidebar.warning(f"Delete '{get_truncated_name(st.session_state.confirm_delete)}'?")
#     col_confirm, col_cancel = st.sidebar.columns([0.5, 0.5])
#     if col_confirm.button("✅ Yes"):
#         delete_chat(st.session_state.confirm_delete)
#         st.session_state.confirm_delete = None
#         if st.session_state.loaded_file == st.session_state.confirm_delete:
#             st.session_state.chat_history = []
#         st.rerun()
#     if col_cancel.button("❌ No"):
#         st.session_state.confirm_delete = None
#
# # Chat input
# user_input = st.chat_input("Ask me something...")
#
# if user_input:
#     with st.spinner(f"{active_model} is working on it"):
#         # Append user message
#         add_message_to_history("user", user_input, st.session_state.chat_history)
#
#         # Get the last 20 messages to pass to the LLM
#         last_20_messages = get_last_n_messages(st.session_state.chat_history, 20)
#
#         # Prepare the context for the agent
#         context = "\n".join([f"{role}: {message}" for role, message in last_20_messages])
#
#         # Agent response
#         response = agent_executor.invoke({"input": context})
#         print(f"\n\nRaw LLM reponse: {response}")
#         reply = response.get("output", "")
#
#         ## Removing reasoning tags
#         cleaned_reply = re.sub(r"<think>.*?</think>", "", reply, flags=re.DOTALL).strip()
#
#         add_message_to_history("agent", cleaned_reply, st.session_state.chat_history)
#
#         # Save chat
#         first_message = st.session_state.chat_history[0][1] if st.session_state.chat_history else "chat"
#         filename_base = "_".join(first_message.strip().lower().split()[:5])
#         save_chat(filename_base.replace(" ", "_"), st.session_state.chat_id, st.session_state.chat_history)
#
# # Display messages
# # Display chat messages
# for role, msg in st.session_state.chat_history:
#     avatar = agent_image if role == "agent" else user_image
#     with st.chat_message(role, avatar=avatar):
#         st.markdown(msg)
#
# # Image upload inside assistant chat bubble
# if "pending_product" in st.session_state:
#     with st.chat_message("assistant", avatar=agent_image):
#         st.info("Finish product creation by uploading an image:")
#         image_file = st.file_uploader("Upload Product Image", type=["jpg", "jpeg", "png"], key="product_image_upload")
#
#         if image_file:
#             try:
#                 image_url = upload_image_to_cloudinary(image_file)
#                 if not image_url:
#                     st.error("❌ Failed to upload image. Please try again with a different file.")
#                 else:
#                     try:
#                         product_id = finalize_product_upload(st.session_state["pending_product"], image_url)
#                         if product_id.startswith("Error"):
#                             st.error(f"❌ Product creation failed: {product_id}")
#                         else:
#                             # st.success(f"Product created successfully with ID: `{product_id}`")
#                             add_message_to_history("agent", f"Product created successfully with ID: `{product_id}`", st.session_state.chat_history)
#
#                             del st.session_state["pending_product"]
#                     except Exception as e:
#                         st.error(f"❌ Unexpected error during product creation: {e}")
#             except Exception as e:
#                 st.error(f"❌ Image upload failed due to an unexpected error: {e}")
# elif "pending_creative" in st.session_state:
#     with st.chat_message("assistant"):
#         st.info("Upload an image to complete the ad creative:")
#         image_file = st.file_uploader("Upload Ad Image", type=["jpg", "jpeg", "png"], key="creative_image_upload")
#
#         if image_file:
#             try:
#                 image_hash = upload_image_to_facebook(
#                     ad_account_id=st.session_state.pending_creative["ad_account_id"],
#                     image_file=image_file
#                 )
#                 if not image_hash:
#                     st.error("❌ Failed to upload image.")
#                 else:
#                     creative_id = finalize_creative_upload(st.session_state["pending_creative"], image_hash)
#                     if isinstance(creative_id, str) and creative_id.startswith("Error"):
#                         st.error(creative_id)
#                     else:
#                         st.success(f"🎯 Creative created successfully with ID: `{creative_id}`")
#                         del st.session_state["pending_creative"]
#             except Exception as e:
#                 st.error(f"❌ Unexpected error: {e}")
#
import json
# import re
# import uuid
# import streamlit as st
# import threading
# import queue
# import json
# import os
# from vosk import Model, KaldiRecognizer, SetLogLevel
# from gtts import gTTS
# import base64
# from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase
#
# # Adjust these paths relative to your app.py if needed
# from app.history.chat_history import delete_chat, get_truncated_name, save_chat, get_chat_files, load_chat, \
#     add_message_to_history, get_last_n_messages
# from app.utils.agent import agent_executor
# from app.utils.facebook.creative_creation import upload_image_to_facebook, finalize_creative_upload
# from app.utils.facebook.product_creation import upload_image_to_cloudinary, finalize_product_upload
# from config.settings import meta_image, agent_image, user_image, active_model
#
# # --- Streamlit UI ---
# st.set_page_config(page_title="Meta Assistant", page_icon=agent_image, layout="wide")
#
# # --- Vosk Model Loading ---
# MODEL_PATH = "vosk_model"  # Ensure this path is correct
# SetLogLevel(-1)  # Suppress Vosk logs
#
# vosk_model = None
# try:
#     if os.path.exists(MODEL_PATH):
#         vosk_model = Model(MODEL_PATH)
#     else:
#         st.error(f"Vosk model not found at '{MODEL_PATH}'. Please download it from https://alphacephei.com/vosk/models and unzip it.")
# except Exception as e:
#     st.error(f"Error loading Vosk model: {e}")
#
# # --- Global Queues for STT and TTS ---
# # Queue for audio frames from webrtc to Vosk
# audio_q = queue.Queue()
# # Event to signal Vosk thread to stop (not strictly used with current WebRTC setup but good practice)
# stop_vosk_thread_event = threading.Event()
# # Thread for Vosk processing
# vosk_recognition_thread = None
#
#
#
# col1, col2 = st.columns([1, 5])
# with col1:
#     st.image(image=meta_image, output_format="PNG", width=120)
# with col2:
#     st.title("AI Based Meta Campaign Assistant")
#
# st.header("Type below or speak to get Started")
#
# # Session state initialization
# if "chat_history" not in st.session_state:
#     st.session_state.chat_history = []
# if "chat_id" not in st.session_state:
#     st.session_state.chat_id = str(uuid.uuid4())
# if "confirm_delete" not in st.session_state:
#     st.session_state.confirm_delete = None
# if "loaded_file" not in st.session_state:
#     st.session_state.loaded_file = None
# if "stt_text_input" not in st.session_state:
#     st.session_state.stt_text_input = ""
# if "tts_enabled" not in st.session_state:
#     st.session_state.tts_enabled = False
# if "is_listening" not in st.session_state:
#     st.session_state.is_listening = False
# if "partial_transcript" not in st.session_state:
#     st.session_state.partial_transcript = ""
#
# # --- Sidebar Controls ---
# with st.sidebar:
#     st.header("Settings")
#
#     # New Chat Button
#     if st.button("➕ Start New Chat"):
#         st.session_state.chat_history = []
#         st.session_state.chat_id = str(uuid.uuid4())
#         st.session_state.loaded_file = None
#         st.session_state.stt_text_input = "" # Clear STT input
#         st.session_state.partial_transcript = "" # Clear partial transcript
#         st.session_state.is_listening = False # Ensure listening state is reset
#         st.rerun()
#
#     st.subheader("💬 Previous Chats")
#     chat_files = get_chat_files()
#
#     for file in chat_files:
#         chat_title = get_truncated_name(file.rsplit("_", 1)[0].replace("_", " "))
#         col1, col2 = st.columns([1, 0.2])
#
#         if col1.button(chat_title, key=f"load_{file}", use_container_width=True):
#             data = load_chat(file)
#             st.session_state.chat_history = data["messages"]
#             st.session_state.chat_id = file.rsplit("_", 1)[-1].replace(".json", "")
#             st.session_state.loaded_file = file
#             st.session_state.stt_text_input = "" # Clear STT input when loading chat
#             st.session_state.partial_transcript = "" # Clear partial transcript
#             st.session_state.is_listening = False # Ensure listening state is reset
#             st.rerun()
#
#         if col2.button("🗑", key=f"delete_{file}"):
#             st.session_state.confirm_delete = file
#
#     # Confirm deletion
#     if st.session_state.confirm_delete:
#         st.warning(f"Delete '{get_truncated_name(st.session_state.confirm_delete)}'?")
#         col_confirm, col_cancel = st.columns([0.5, 0.5])
#         if col_confirm.button("✅ Yes"):
#             delete_chat(st.session_state.confirm_delete)
#             st.session_state.confirm_delete = None
#             if st.session_state.loaded_file == st.session_state.confirm_delete:
#                 st.session_state.chat_history = []
#             st.rerun()
#         if col_cancel.button("❌ No"):
#             st.session_state.confirm_delete = None
#
#     st.markdown("---")
#     st.subheader("Speech & Voice")
#     st.session_state.tts_enabled = st.checkbox("🔊 Enable Text-to-Speech Output", value=st.session_state.tts_enabled)
#
#
# # --- Speech-to-Text (Vosk Integration with streamlit-webrtc) ---
#
# class VoskAudioProcessor(AudioProcessorBase):
#     def __init__(self, model):
#         self.model = model
#         self.recognizer = KaldiRecognizer(model, 16000) # Vosk models are usually 16kHz
#         self.partial_queue = audio_q # Use the global audio_q for recognized parts
#
#     def recv(self, frame):
#         audio_chunk = frame.to_ndarray().tobytes()
#         if self.recognizer.AcceptWaveform(audio_chunk):
#             result = json.loads(self.recognizer.Result())
#             if result.get('text'):
#                 self.partial_queue.put({"type": "final", "text": result['text']})
#         else:
#             partial_result = json.loads(self.recognizer.PartialResult())
#             if partial_result.get('partial'):
#                 self.partial_queue.put({"type": "partial", "text": partial_result['partial']})
#         return frame # Return frame to keep the stream alive
#
# # Function to process Vosk queue updates and update Streamlit state
# def vosk_update_state():
#     while not audio_q.empty():
#         try:
#             message = audio_q.get_nowait()
#             if message["type"] == "partial":
#                 st.session_state.partial_transcript = message["text"]
#             elif message["type"] == "final":
#                 st.session_state.stt_text_input += message["text"] + " "
#                 st.session_state.partial_transcript = "" # Clear partial
#             st.rerun()
#         except queue.Empty:
#             pass
#
# # Placeholder for webrtc_streamer to control its visibility
# webrtc_placeholder = st.empty()
#
# # --- Chat Input with Voice Button ---
# chat_input_col, voice_button_col = st.columns([5, 1])
#
# with chat_input_col:
#     user_input = st.chat_input(
#         "Ask me something...",
#         key="main_chat_input"
#     )
#
#     # Display partial transcript (if listening)
#     if st.session_state.is_listening and st.session_state.partial_transcript:
#         st.markdown(f"**Live Transcript:** *{st.session_state.partial_transcript}*")
#     elif st.session_state.is_listening:
#         st.markdown(f"**Live Transcript:** *Say something...*")
#
#     # Display the full recognized text for manual copy/paste
#     if not st.session_state.is_listening and st.session_state.stt_text_input:
#         st.info(f"**Recognized Text (copy/paste into chat):**\n`{st.session_state.stt_text_input.strip()}`")
#
#
# with voice_button_col:
#     # Voice input button
#     if vosk_model:
#         if st.button("🎤 Start Voice" if not st.session_state.is_listening else "🛑 Stop Voice", use_container_width=True):
#             if not st.session_state.is_listening:
#                 st.session_state.is_listening = True
#                 st.session_state.stt_text_input = "" # Clear input on start
#                 st.session_state.partial_transcript = "" # Clear partial transcript
#                 st.rerun()
#             else:
#                 st.session_state.is_listening = False
#                 # Finalize any remaining partial transcript when stopping
#                 if st.session_state.partial_transcript:
#                     st.session_state.stt_text_input += st.session_state.partial_transcript + " "
#                     st.session_state.partial_transcript = ""
#                 st.rerun()
#     else:
#         st.warning("Vosk model not loaded. Voice input disabled.")
#
#
# # Conditionally render webrtc_streamer
# if st.session_state.is_listening and vosk_model:
#     with webrtc_placeholder: # This makes the component invisible
#         webrtc_ctx = webrtc_streamer(
#             key="speech_recognition",
#             mode=WebRtcMode.SENDONLY,
#             audio_processor_factory=lambda: VoskAudioProcessor(vosk_model),
#             rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
#             media_stream_constraints={"video": False, "audio": True},
#             async_processing=True,
#         )
#
# # Call the update function to process Vosk queue and update UI
# vosk_update_state()
#
#
# # Clear STT text input after user input is taken
# # This ensures it clears *after* the user has had a chance to see/copy it.
# # However, if user_input is directly from keyboard, stt_text_input won't be used.
# # The `st.info` box will handle visibility of recognized text.
# # The key is to manage when stt_text_input is actually cleared for a new voice session.
# # The current logic (`if not st.session_state.is_listening and st.session_state.stt_text_input:`) for
# # displaying the recognized text and clearing on new voice start is good.
# # Let's re-evaluate if this specific 'if user_input and st.session_state.stt_text_input:' is still needed
# # or if it might prematurely clear text the user *just* wants to see.
# # For now, keeping it as it was intended to clear after a message was sent,
# # but the primary interaction is now manual copy/paste for STT.
# if user_input and st.session_state.stt_text_input:
#     # This line might clear the STT input too soon if the user typed something
#     # that wasn't the STT result. Consider removing this line if the
#     # STT display (st.info) is sufficient.
#     st.session_state.stt_text_input = ""
#
#
# if user_input:
#     with st.spinner(f"{active_model} is working on it"):
#         # Append user message
#         add_message_to_history("user", user_input, st.session_state.chat_history)
#
#         # Get the last 20 messages to pass to the LLM
#         last_20_messages = get_last_n_messages(st.session_state.chat_history, 20)
#
#         # Prepare the context for the agent
#         context = "\n".join([f"{role}: {message}" for role, message in last_20_messages])
#
#         # Agent response
#         response = agent_executor.invoke({"input": context})
#         print(f"\n\nRaw LLM reponse: {response}")
#         reply = response.get("output", "")
#
#         ## Removing reasoning tags
#         cleaned_reply = re.sub(r"<think>.*?</think>", "", reply, flags=re.DOTALL).strip()
#
#         add_message_to_history("agent", cleaned_reply, st.session_state.chat_history)
#
#         # Trigger TTS if enabled
#         if st.session_state.tts_enabled and cleaned_reply:
#             try:
#                 tts = gTTS(text=cleaned_reply, lang='en')
#                 # Save to a temporary file
#                 audio_file_path = "temp_response.mp3"
#                 tts.save(audio_file_path)
#
#                 # Play audio in Streamlit
#                 audio_bytes = open(audio_file_path, 'rb').read()
#                 st.audio(audio_bytes, format="audio/mp3", autoplay=True, loop=False)
#
#                 # Clean up the temporary file
#                 os.remove(audio_file_path)
#             except Exception as e:
#                 st.error(f"Error generating or playing speech: {e}")
#
#
#         # Save chat
#         first_message = st.session_state.chat_history[0][1] if st.session_state.chat_history else "chat"
#         filename_base = "_".join(first_message.strip().lower().split()[:5])
#         save_chat(filename_base.replace(" ", "_"), st.session_state.chat_id, st.session_state.chat_history)
#
# # Display messages
# for role, msg in st.session_state.chat_history:
#     avatar = agent_image if role == "agent" else user_image
#     with st.chat_message(role, avatar=avatar):
#         st.markdown(msg)
#
# # Image upload inside assistant chat bubble
# if "pending_product" in st.session_state:
#     with st.chat_message("assistant", avatar=agent_image):
#         st.info("Finish product creation by uploading an image:")
#         image_file = st.file_uploader("Upload Product Image", type=["jpg", "jpeg", "png"], key="product_image_upload")
#
#         if image_file:
#             try:
#                 image_url = upload_image_to_cloudinary(image_file)
#                 if not image_url:
#                     st.error("❌ Failed to upload image. Please try again with a different file.")
#                 else:
#                     try:
#                         product_id = finalize_product_upload(st.session_state["pending_product"], image_url)
#                         if product_id.startswith("Error"):
#                             st.error(f"❌ Product creation failed: {product_id}")
#                         else:
#                             add_message_to_history("agent", f"Product created successfully with ID: `{product_id}`", st.session_state.chat_history)
#                             del st.session_state["pending_product"]
#                             # Trigger TTS if enabled
#                             if st.session_state.tts_enabled:
#                                 try:
#                                     tts = gTTS(text=f"Product created successfully with ID: {product_id}", lang='en')
#                                     audio_file_path = "temp_response.mp3"
#                                     tts.save(audio_file_path)
#                                     audio_bytes = open(audio_file_path, 'rb').read()
#                                     st.audio(audio_bytes, format="audio/mp3", autoplay=True, loop=False)
#                                     os.remove(audio_file_path)
#                                 except Exception as e:
#                                     st.error(f"Error playing TTS for product ID: {e}")
#                     except Exception as e:
#                         st.error(f"❌ Unexpected error during product creation: {e}")
#             except Exception as e:
#                 st.error(f"❌ Image upload failed due to an unexpected error: {e}")
# elif "pending_creative" in st.session_state:
#     with st.chat_message("assistant"):
#         st.info("Upload an image to complete the ad creative:")
#         image_file = st.file_uploader("Upload Ad Image", type=["jpg", "jpeg", "png"], key="creative_image_upload")
#
#         if image_file:
#             try:
#                 image_hash = upload_image_to_facebook(
#                     ad_account_id=st.session_state.pending_creative["ad_account_id"],
#                     image_file=image_file
#                 )
#                 if not image_hash:
#                     st.error("❌ Failed to upload image.")
#                 else:
#                     creative_id = finalize_creative_upload(st.session_state["pending_creative"], image_hash)
#                     if isinstance(creative_id, str) and creative_id.startswith("Error"):
#                         st.error(creative_id)
#                     else:
#                         st.success(f"🎯 Creative created successfully with ID: `{creative_id}`")
#                         add_message_to_history("agent", f"Creative created successfully with ID: `{creative_id}`", st.session_state.chat_history)
#                         del st.session_state["pending_creative"]
#                         # Trigger TTS if enabled
#                         if st.session_state.tts_enabled:
#                             try:
#                                 tts = gTTS(text=f"Creative created successfully with ID: {creative_id}", lang='en')
#                                 audio_file_path = "temp_response.mp3"
#                                 tts.save(audio_file_path)
#                                 audio_bytes = open(audio_file_path, 'rb').read()
#                                 st.audio(audio_bytes, format="audio/mp3", autoplay=True, loop=False)
#                                 os.remove(audio_file_path)
#                             except Exception as e:
#                                 st.error(f"Error playing TTS for creative ID: {e}")
#             except Exception as e:
#                 st.error(f"❌ Unexpected error: {e}")


import re
import uuid
import streamlit as st
from streamlit.components.v1 import html

from app.history.chat_history import delete_chat, get_truncated_name, save_chat, get_chat_files, load_chat, \
    add_message_to_history, get_last_n_messages
from app.utils.agent import agent_executor
from app.utils.facebook.creative_creation import upload_image_to_facebook, finalize_creative_upload
from app.utils.facebook.product_creation import upload_image_to_cloudinary, finalize_product_upload
from app.utils.voice.stt import stt_data
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
if "voice_mode" not in st.session_state:
    st.session_state.voice_mode = False

# # JavaScript for TTS
# tts_js = """
# <script>
# function speak(text) {
#     const utterance = new SpeechSynthesisUtterance(text);
#     window.speechSynthesis.speak(utterance);
# }
# </script>
# """
#
# # Inject TTS JavaScript
# st.components.v1.html(tts_js, height=0)
#
#
# # Function to speak text
# def speak(text):
#     # if st.session_state.voice_mode:
#         js = f"""
#         <script>
#             console.log('Speaking:', "{text}");
#             const utterance = new SpeechSynthesisUtterance("{text}");
#             window.speechSynthesis.speak(utterance);
#         </script>
#         """
#         st.components.v1.html(js, height=0)


def speak(text: str):
    # Clean and prepare text
    safe_text = re.sub(r"[^\x20-\x7E]+", " ", text).strip()  # remove non-printable chars

    safe_text_without_numbers = re.sub(r"\b\d{6,}\b", "", safe_text)

    url_pattern = r"(?:https?://|www\.)\S+|(?:\S+\.[a-z]{2,})/\S*"  # This is a more comprehensive URL pattern

    safe_text_without_urls = re.sub(url_pattern, "", safe_text_without_numbers)

    js_safe_text = json.dumps(safe_text_without_urls)  # safely escape quotes, newlines, etc.

    # Inject TTS JS and call it
    st.components.v1.html(f"""
    <script>
    const speak = (text) => {{
        if (window.speechSynthesis.speaking) {{
            window.speechSynthesis.cancel();
        }}
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = "en-US";
        window.speechSynthesis.speak(utterance);
    }};
    speak({js_safe_text});
    </script>
    """, height=0)




# New Chat Button
if st.sidebar.button("➕ Start New Chat",use_container_width=True):
    st.session_state.chat_history = []
    st.session_state.chat_id = str(uuid.uuid4())
    st.session_state.loaded_file = None
    st.rerun()

# Sidebar - Voice Mode Toggle (TTS only)
st.session_state.voice_mode = st.sidebar.toggle("🔊 Voice Responses", value=st.session_state.voice_mode,
                                                help="Enable text-to-speech for assistant responses")

# Sidebar - Previous chats
st.sidebar.subheader("💬 Previous Chats")

chat_files = get_chat_files()

for file in chat_files:
    chat_title = get_truncated_name(file.rsplit("_", 1)[0].replace("_", " "))
    col1, col2 = st.sidebar.columns([1, 0.2])

    if col1.button(chat_title, key=f"load_{file}", use_container_width=True):
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
    col_confirm, col_cancel = st.sidebar.columns([1, 1])
    if col_confirm.button("✅ Yes",use_container_width=True):
        delete_chat(st.session_state.confirm_delete)
        st.session_state.confirm_delete = None
        if st.session_state.loaded_file == st.session_state.confirm_delete:
            st.session_state.chat_history = []
        st.rerun()
    if col_cancel.button("❌ No",use_container_width=True):
        st.session_state.confirm_delete = None


# col1, col2 = st.columns([1, 0.2])
# with col1:
#     user_input = st.chat_input("Ask me something...")
#
# if col2.button("🎙️"):
#     user_input = "how ARE you?"
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

        # Speak the response if voice mode is on
        if st.session_state.voice_mode:
            speak(cleaned_reply)

        add_message_to_history("agent", cleaned_reply, st.session_state.chat_history)

        # Save chat
        first_message = st.session_state.chat_history[0][1] if st.session_state.chat_history else "chat"
        filename_base = "_".join(first_message.strip().lower().split()[:5])
        save_chat(filename_base.replace(" ", "_"), st.session_state.chat_id, st.session_state.chat_history)


# # Display messages
# for role, msg in st.session_state.chat_history:
#     avatar = agent_image if role == "agent" else user_image
#     with st.chat_message(role, avatar=avatar):
#         st.markdown(msg)

for i, (role, msg) in enumerate(st.session_state.chat_history):
    avatar = agent_image if role == "agent" else user_image
    with st.chat_message(role, avatar=avatar):
        cols = st.columns([0.95, 0.05]) if role == "agent" else [st.container()]
        with cols[0] if role == "agent" else cols[0]:
            st.markdown(msg)
        if role == "agent":
            with cols[1]:
                if st.button("🔊", key=f"speak_{i}"):
                    speak(msg)

## Injecting STT code
html(stt_data)



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
                            add_message_to_history("agent", f"Product created successfully with ID: `{product_id}`",
                                                   st.session_state.chat_history)
                            speak(f"Product created successfully with ID: {product_id}")
                            del st.session_state["pending_product"]
                    except Exception as e:
                        st.error(f"❌ Unexpected error during product creation: {e}")
            except Exception as e:
                st.error(f"❌ Image upload failed due to an unexpected error: {e}")
elif "pending_creative" in st.session_state:
    with st.chat_message("assistant"):
        st.info("Upload an image to complete the ad creative:")
        image_file = st.file_uploader("Upload Ad Image", type=["jpg", "jpeg", "png"], key="creative_image_upload")

        if image_file:
            try:
                image_hash = upload_image_to_facebook(
                    ad_account_id=st.session_state.pending_creative["ad_account_id"],
                    image_file=image_file
                )
                if not image_hash:
                    st.error("❌ Failed to upload image.")
                else:
                    creative_id = finalize_creative_upload(st.session_state["pending_creative"], image_hash)
                    if isinstance(creative_id, str) and creative_id.startswith("Error"):
                        st.error(creative_id)
                    else:
                        st.success(f"🎯 Creative created successfully with ID: `{creative_id}`")
                        add_message_to_history("agent", f"Creative created successfully with ID: `{creative_id}`",
                                               st.session_state.chat_history)
                        speak(f"Creative created successfully with ID: {creative_id}")
                        del st.session_state["pending_creative"]
            except Exception as e:
                st.error(f"❌ Unexpected error: {e}")