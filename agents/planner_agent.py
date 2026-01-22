from langchain.agents import create_agent
from config import get_llm, get_memory

def create_planner_agent(debug=False):
    """
    Breaks complex questions into sub-questions so it's easier to understand
    """
    
    llm = get_llm()
    memory = get_memory()

    tools = []

    agent = create_agent(llm, tools, checkpointer=memory, debug=debug, system_prompt = "You are a research planning assistant. Your job is to break down complex research questions into 3-5 focused sub-questions.")

    return agent, memory
