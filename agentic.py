from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_community.agent_toolkits.load_tools import load_tools
from langgraph.checkpoint.memory import MemorySaver
from langchain.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
import requests
from bs4 import BeautifulSoup

load_dotenv()

@tool
def web_search(query: str) -> str:
    """Useful for searching the web for current information or recent events"""
    search = DuckDuckGoSearchRun()
    results = search.run(query)
    return results

@tool
def fetch_webpage(url: str) -> str:
    """Fetches and extracts text content from a webpage URL"""
    response = requests.get(url).text
    soup = BeautifulSoup(response, "html.parser")

    text = soup.get_text()[:5000]
    return text


# Create memory for the agent
memory = MemorySaver()

prompt = "What are the latest tech news headlines today?"

llm = ChatOpenAI(temperature=0, model='gpt-3.5-turbo')

tools = load_tools(['wikipedia', "llm-math"], llm=llm)
tools.extend([web_search, fetch_webpage])

# Create agent with memory using checkpointer parameter
agent = create_agent(llm, tools, checkpointer=memory, debug=False)

config = {"configurable": {"thread_id": "conversation-1"}}

inputs = {"messages": [{"role": "user", "content": prompt}]}
result = agent.invoke(inputs, config)

final_message = result['messages'][-1]
print(final_message.content)

    




