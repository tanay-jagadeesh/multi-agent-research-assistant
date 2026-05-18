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
    agent = create_agent(llm, tools, checkpointer=memory, debug=debug, system_prompt="""You are a research assistant. You will receive a list of sub-questions.

For each question:
1. Use the web_search tool to find relevant information
2. For the most useful results, use fetch_webpage to get more detail
3. Record the source URL alongside every fact you find

Return findings in this EXACT format:

Question 1: [question]
Findings:
- [finding 1] (Source: https://example.com/page)
- [finding 2] (Source: https://another.com/article)

Question 2: [question]
Findings:
- [finding] (Source: https://url.com)

IMPORTANT: Every bullet point MUST end with (Source: URL) using the real URL from your search results. Never omit the source URL.""")

    return agent, memory
