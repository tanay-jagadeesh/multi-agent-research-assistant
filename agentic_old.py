from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_community.agent_toolkits.load_tools import load_tools
from langgraph.checkpoint.memory import MemorySaver
from langchain.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
import os
import requests
from bs4 import BeautifulSoup
import logging

load_dotenv()

SEARCH_PROVIDER = os.getenv("SEARCH_PROVIDER", "duckduckgo")

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s' 
)

@tool
def web_search(query: str) -> str:
    """Useful for searching the web for current information or recent events"""
    logging.info(f"Web search called with query: {query}")
    if SEARCH_PROVIDER == "tavily":
        from tavily import TavilyClient
        client = TavilyClient()
        response = client.search(query=query, max_results=5)
        results = "\n\n".join(
            f"{r['title']}: {r['content']}" for r in response["results"]
        )
    else:
        search = DuckDuckGoSearchRun()
        results = search.run(query)
    logging.info("Web search completed successfully")
    return results

@tool
def fetch_webpage(url: str) -> str:
    """Fetches and extracts text content from a webpage URL"""
    logging.info(f"Fetching webpage: {url}")
    try:
        response = requests.get(url).text
        soup = BeautifulSoup(response, "html.parser")

        text = soup.get_text()[:5000]
        logging.info("Webpage fetched successfully")
        return text
    except requests.exceptions.ConnectionError as e:
        logging.error(f"Connection error: {e}")
        return "Error: Invalid URL or could not connect"
    except Exception as e:
        logging.error(f"Error fetching webpage: {e}")
        return f"Error fetching website: {e}"
@tool
def summarize(text:str) -> str:
    """Summarizes text in longer formats such as articles"""
    logging.info("Summarizing text")
    prompt = f"Summarize this text {text}"

    llm = ChatOpenAI(temperature = 0, model = "gpt-3.5-turbo")
    result = llm.invoke(prompt)
    logging.info("Text summarized successfully")
    return result

@tool
def file_saver(text:str) -> str:
    """Saves text from summarize function to a file"""
    logging.info("Saving text to file")
    with open("info.txt", "w") as f:
       result = f.write(text)
    logging.info("File saved successfully")
    return "File Saved Successfully"

# Create memory for the agent
memory = MemorySaver()

prompt = "What are the latest tech news headlines today?"

llm = ChatOpenAI(temperature=0, model='gpt-3.5-turbo')

tools = load_tools(['wikipedia', "llm-math"], llm=llm)
tools.extend([web_search, fetch_webpage, summarize, file_saver])

# Create agent with memory using checkpointer parameter
agent = create_agent(llm, tools, checkpointer=memory, debug=False)

config = {"configurable": {"thread_id": "conversation-1"}}

inputs = {"messages": [{"role": "user", "content": prompt}]}
result = agent.invoke(inputs, config)

final_message = result['messages'][-1]
print(final_message.content)

    




