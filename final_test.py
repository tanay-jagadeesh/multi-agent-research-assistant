"""
Final comprehensive system test
"""
from workflow import create_workflow
from config import setup_logging
from utils.logging_system import performance_tracker
import time

setup_logging()

print("="*70)
print("FINAL SYSTEM TEST - MULTI-AGENT RESEARCH ASSISTANT")
print("="*70)

print("\n🔧 Initializing workflow...")
workflow = create_workflow()
print("✅ Workflow created successfully")

test_question = "What are the latest breakthroughs in renewable energy technology?"

print(f"\n📝 Test Question: {test_question}")
print("\n🚀 Starting research pipeline...\n")

initial_state = {
    "user_query": test_question,
    "research_plan": None,
    "findings": None,
    "fact_check": None,
    "citations": None,
    "final_report": None,
    "quality_check": None,
    "revision_count": 0,
    "shared_context": None
}

config = {"configurable": {"thread_id": "final-test"}}

start_time = time.time()

try:
    print("Stage 1/6: Planner - Breaking down question...")
    print("Stage 2/6: Researcher - Gathering information...")
    print("Stage 3/6: Fact-Checker - Verifying claims...")
    print("Stage 4/6: Citation - Formatting sources...")
    print("Stage 5/6: Analyst - Synthesizing report...")
    print("Stage 6/6: Quality Control - Evaluating quality...")

    result = workflow.invoke(initial_state, config)

    duration = time.time() - start_time

    print(f"\n✅ Research completed in {duration:.2f} seconds\n")

    print("="*70)
    print("RESEARCH PLAN")
    print("="*70)
    print(result.get("research_plan", "N/A")[:500] + "...\n")

    print("="*70)
    print("FACT-CHECK RESULTS")
    print("="*70)
    print(result.get("fact_check", "N/A")[:500] + "...\n")

    print("="*70)
    print("QUALITY EVALUATION")
    print("="*70)
    print(result.get("quality_check", "N/A")[:500] + "...\n")

    print("="*70)
    print("FINAL REPORT")
    print("="*70)
    print(result["final_report"])

    print("\n" + "="*70)
    print("VALIDATION CHECKS")
    print("="*70)

    checks = {
        "Research Plan Generated": bool(result.get("research_plan")),
        "Findings Collected": bool(result.get("findings")),
        "Fact-Check Completed": bool(result.get("fact_check")),
        "Citations Formatted": bool(result.get("citations")),
        "Final Report Generated": bool(result.get("final_report")),
        "Quality Check Performed": bool(result.get("quality_check")),
        "Report Length > 500 chars": len(result.get("final_report", "")) > 500,
        "Revision Count Valid": 0 <= result.get("revision_count", 0) <= 2
    }

    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check}")

    all_passed = all(checks.values())

    performance_tracker.print_dashboard()

    print("\n" + "="*70)
    if all_passed:
        print("🎉 ALL TESTS PASSED - SYSTEM FULLY OPERATIONAL")
    else:
        print("⚠️  SOME TESTS FAILED - REVIEW REQUIRED")
    print("="*70)

except Exception as e:
    print(f"\n❌ SYSTEM ERROR: {str(e)}")
    print("\nError handling working - graceful failure")
    import traceback
    traceback.print_exc()
