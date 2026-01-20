"""
Main entry point for the research assistant.
"""
from config import setup_logging
from agents import create_research_agent

def run_research(query: str, thread_id: str = "conversation-1", debug: bool = False):
    """
    Run a research query through the agent.

    Args:
        query: The research question or task
        thread_id: Conversation thread ID for memory persistence
        debug: Enable debug mode

    Returns:
        Agent response
    """
    agent, memory = create_research_agent(debug=debug)

    config = {"configurable": {"thread_id": thread_id}}
    inputs = {"messages": [{"role": "user", "content": query}]}

    result = agent.invoke(inputs, config)
    final_message = result['messages'][-1]

    return final_message.content

def main():
    """Main function to run the research assistant."""
    # Setup logging
    setup_logging()

    # Example query
    prompt = "What are the latest tech news headlines today?"

    print("Research Assistant Starting...")
    print(f"Query: {prompt}\n")

    result = run_research(prompt, debug=False)

    print("\n" + "="*50)
    print("RESULT:")
    print("="*50)
    print(result)

if __name__ == "__main__":
    main()
