"""
Main entry point for the research assistant.
"""
from config import setup_logging
from workflow import create_workflow


def run_research(query: str, thread_id: str = "workflow-1"):
    """
    Run a research query through the complete workflow.

    Args:
        query: The research question
        thread_id: Workflow thread ID for memory persistence

    Returns:
        Final report from analyst agent
    """
    workflow = create_workflow()

    initial_state = {
        "user_query": query,
        "research_plan": None,
        "findings": None,
        "fact_check": None,
        "final_report": None
    }

    config = {"configurable": {"thread_id": thread_id}}

    result = workflow.invoke(initial_state, config)

    return result["final_report"]


def main():
    """Main function to run the research assistant."""
    setup_logging()

    prompt = "What is the future of Artificial Intelligence in Healthcare?"

    print("Research Assistant Starting...")
    print(f"Query: {prompt}\n")

    result = run_research(prompt)

    print("FINAL REPORT:")
    print("="*50)
    print(result)


if __name__ == "__main__":
    main()
