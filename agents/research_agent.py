from langchain.agents import create_agent
from tools import web_search, fetch_webpage
from config import get_llm, get_memory

def create_research_agent(debug=False):
    """
    Create a research agent with all available tools.
    """
    llm = get_llm()
    memory = get_memory()

    # Load base tools
    tools = ([web_search, fetch_webpage])

    # Create agent with memory
    agent = create_agent(llm, tools, checkpointer=memory, debug=debug)

    return agent, memory
