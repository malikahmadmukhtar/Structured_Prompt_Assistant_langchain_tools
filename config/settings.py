from langchain.agents import AgentType
import os
from dotenv import load_dotenv
load_dotenv()

active_model='deepseek-r1-distill-llama-70b'
temperature=0.3
CHAT_DIR = "chat_logs"
agent_type=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION
groq_api_key=os.getenv("GROQ_API_KEY")