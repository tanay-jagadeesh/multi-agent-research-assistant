from langchain.agents import create_agent
from langchain_community.agent_toolkits.load_tools import load_tools
from tools import web_search, fetch_webpage, summarize, file_saver
from config import get_llm, get_memory

def create_research_agent(debug=False):
    """
    Create a research agent with all available tools.

    Args:
        debug: Enable debug mode for verbose output

    Returns:
        Configured agent and memory
    """
    llm = get_llm()
    memory = get_memory()

    # Load base tools
    tools = load_tools(['wikipedia', 'llm-math'], llm=llm)

    # Add custom tools
    tools.extend([web_search, fetch_webpage, summarize, file_saver])

    # Create agent with memory
    agent = create_agent(llm, tools, checkpointer=memory, debug=debug)

    return agent, memory
