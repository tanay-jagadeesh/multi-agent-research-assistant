from tools import web_search
from langchain.agents import create_agent
from config import get_llm, get_memory

def create_searcher_agent(debug=False):
    """
    Create a searcher agent that finds 3-5 relevant URLs for a topic.

    Args:
        debug: Enable debug mode for verbose output

    Returns:
        Configured agent and memory
    """
    llm = get_llm()
    memory = get_memory()

    tools = [web_search]

    agent = create_agent(llm, tools, checkpointer=memory, debug=debug)

    return agent, memory
