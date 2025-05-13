import os
import json
from config.settings import CHAT_DIR

# --- STORAGE UTILS ---
os.makedirs(CHAT_DIR, exist_ok=True)

def get_chat_files():
    return sorted([f for f in os.listdir(CHAT_DIR) if f.endswith(".json")], reverse=True)

def save_chat(name, chat_id, messages):
    filename = os.path.join(CHAT_DIR, f"{name}_{chat_id}.json")
    with open(filename, "w") as f:
        json.dump({"messages": messages}, f)

def load_chat(filename):
    with open(os.path.join(CHAT_DIR, filename), "r") as f:
        return json.load(f)

def delete_chat(filename):
    os.remove(os.path.join(CHAT_DIR, filename))

def get_truncated_name(name):
    return (name[:20] + "...") if len(name) > 20 else name

# --- MEMORY MANAGEMENT FUNCTIONS ---
def add_message_to_history(role, message, history):
    """Adds a message to the chat history."""
    history.append((role, message))

def get_last_n_messages(history, n=20):
    """Returns the last n messages from the history."""
    return history[-n:]

