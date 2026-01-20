from langchain.tools import tool
from langchain_openai import ChatOpenAI
import logging

@tool
def summarize(text: str) -> str:
    """Summarizes text in longer formats such as articles"""
    logging.info("Summarizing text")
    prompt = f"Summarize this text: {text}"

    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
    result = llm.invoke(prompt)
    logging.info("Text summarized successfully")
    return result.content
