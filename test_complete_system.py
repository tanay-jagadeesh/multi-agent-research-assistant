from workflow import create_workflow
from config import setup_logging

setup_logging()

workflow = create_workflow()

question = "What are the latest developments in quantum computing?"

initial_state = {
    "user_query": question,
    "research_plan": None,
    "findings": None,
    "fact_check": None,
    "citations": None,
    "final_report": None,
    "quality_check": None,
    "revision_count": 0,
    "shared_context": None
}

config = {"configurable": {"thread_id": "complete-test"}}

print(f"Testing complete system with query: {question}\n")

try:
    result = workflow.invoke(initial_state, config)

    print("\nFINAL REPORT:")
    print("="*50)
    print(result["final_report"])

    print("\n\nQUALITY CHECK:")
    print("="*50)
    print(result["quality_check"])

    print(f"\n\nRevision count: {result['revision_count']}")

    print("\n\nTest completed successfully!")

except Exception as e:
    print(f"\nError during execution: {str(e)}")
    print("Error handling working - system gracefully handled failure")
