from tools import summarize, fetch_webpage
from langchain.agents import create_agent
from config import get_llm, get_memory

def create_summarizer_agent(debug=False):
    """
    Create a summarizer agent that fetches the url and summarizes the contents.
    """
    
    llm = get_llm()
    memory = get_memory()

    tools = [fetch_webpage, summarize]

    agent = create_agent(llm, tools, checkpointer=memory, debug=debug)

    return agent, memory
