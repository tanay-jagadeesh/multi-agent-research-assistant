from workflow import create_workflow
from config import setup_logging

setup_logging()

workflow = create_workflow()

question = "What are the capabilities of GPT-5?"

initial_state = {
    "user_query": question,
    "research_plan": None,
    "findings": None,
    "fact_check": None,
    "final_report": None
}

config = {"configurable": {"thread_id": "fact-check-test"}}

result = workflow.invoke(initial_state, config)

print("\nRESEARCH PLAN:")
print(result["research_plan"])

print("\nFINDINGS:")
print(result["findings"])

print("\nFACT-CHECK RESULTS:")
print(result["fact_check"])

print("\nFINAL REPORT:")
print(result["final_report"])
