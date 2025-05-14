from langchain.agents import AgentType
import os
from dotenv import load_dotenv

load_dotenv()

## LLM to use
active_model = 'deepseek-r1-distill-llama-70b'

## model temperature
temperature = 0.5

## chat history path
CHAT_DIR = "chat_logs"

## agent type
agent_type = AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION

## groq api setup
groq_api_key = os.getenv("GROQ_API_KEY")

## assets
project_root = os.getcwd()
meta_image = os.path.join(project_root, "assets", "images", "meta.png")
agent_image = os.path.join(project_root, "assets", "images", "agent.png")
user_image = os.path.join(project_root, "assets", "images", "user.png")

## facebook setup
fb_access_token = os.getenv("FB_ACCESS_TOKEN")
fb_base_url = os.getenv("FB_BASE_URL")
