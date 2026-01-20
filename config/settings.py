import logging
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver

# Load environment variables
load_dotenv()

def setup_logging():
    """Configure logging for the application"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def get_llm(temperature=0, model='gpt-3.5-turbo'):
    """Get configured LLM instance"""
    return ChatOpenAI(temperature=temperature, model=model)

def get_memory():
    """Get memory saver for agent state"""
    return MemorySaver()
