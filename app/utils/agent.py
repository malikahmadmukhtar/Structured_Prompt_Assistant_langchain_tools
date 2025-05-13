from langchain.agents import initialize_agent
from app.tools.tool_list import declared_tool_list
from langchain_groq import ChatGroq
from config.agent_prompt import agent_prompt
from config.settings import active_model, temperature, agent_type, groq_api_key

# --- AGENT SETUP ---
llm = ChatGroq(
    temperature=temperature,
    model=active_model,
    api_key=groq_api_key
)


# --- AGENT INITIALIZATION ---
agent_executor = initialize_agent(
    tools=declared_tool_list,
    llm=llm,
    # agent=AgentType.OPENAI_FUNCTIONS,
    agent=agent_type,
    agent_kwargs={
        "system_message": agent_prompt
    },
    verbose=True,
    memory=None,  # No default memory; we'll manage it manually
    handle_parsing_errors=True,
)