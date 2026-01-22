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
    agent = create_agent(llm, tools, checkpointer=memory, debug=debug, system_prompt="You are a research assistant. You will receive a list of sub-questions. For each question: 1) Search for relevant information, 2) Gather key findings. Return your findings in a structured format: 'Question 1: [question]\\nFindings:\\n- [finding 1]\\n- [finding 2]\\n\\nQuestion 2: [question]\\nFindings:'")

    return agent, memory
