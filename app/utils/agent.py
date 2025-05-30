import os
from langchain.agents import initialize_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from app.tools.tool_list import declared_tool_list
from langchain_groq import ChatGroq
from config.settings import active_model, temperature, agent_type, groq_api_key
from dotenv import load_dotenv
load_dotenv()

# --- AGENT SETUP ---
# llm = ChatGroq(
#     temperature=temperature,
#     model=active_model,
#     api_key=groq_api_key
# )

llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.3,
        google_api_key=os.getenv("GEMINI_API_KEY")
)



# --- AGENT INITIALIZATION ---
agent_executor = initialize_agent(
    tools=declared_tool_list,
    llm=llm,
    agent=agent_type,
    verbose=True,
    memory=None,
    handle_parsing_errors=True,
)