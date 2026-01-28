"""
Comprehensive test suite for Multi-Agent Research Assistant
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from workflow import create_workflow
from config import setup_logging
import time

setup_logging()

TEST_QUESTIONS = [
    "What is quantum computing?",
    "Explain climate change causes",
    "How does blockchain work?",
    "What are the benefits of meditation?",
    "Describe the history of the Internet",
    "What is machine learning?",
    "How do vaccines work?",
    "What causes economic recessions?",
    "Explain photosynthesis",
    "What is cryptocurrency?",
    "How does 5G technology work?",
    "What is gene editing?",
    "Explain renewable energy sources",
    "What is artificial general intelligence?",
    "How do neural networks learn?",
    "What is the metaverse?",
    "Explain quantum entanglement",
    "What is dark matter?",
    "How does GPS work?",
    "What is the gut microbiome?"
]


class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.execution_times = []

    def add_pass(self, question, duration):
        self.passed += 1
        self.execution_times.append(duration)
        print(f"✅ PASS: {question} ({duration:.2f}s)")

    def add_fail(self, question, error, duration):
        self.failed += 1
        self.errors.append((question, error))
        print(f"❌ FAIL: {question} ({duration:.2f}s) - {error}")

    def print_summary(self):
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0

        print("\n" + "="*70)
        print("TEST SUITE RESULTS")
        print("="*70)
        print(f"\nTotal Tests: {total}")
        print(f"Passed: {self.passed} ({pass_rate:.1f}%)")
        print(f"Failed: {self.failed}")

        if self.execution_times:
            avg_time = sum(self.execution_times) / len(self.execution_times)
            print(f"\nAverage Execution Time: {avg_time:.2f}s")
            print(f"Fastest: {min(self.execution_times):.2f}s")
            print(f"Slowest: {max(self.execution_times):.2f}s")

        if self.errors:
            print("\n" + "-"*70)
            print("FAILURE ANALYSIS")
            print("-"*70)

            error_types = {}
            for question, error in self.errors:
                error_type = type(error).__name__
                if error_type not in error_types:
                    error_types[error_type] = []
                error_types[error_type].append(question)

            for error_type, questions in error_types.items():
                print(f"\n{error_type}: {len(questions)} occurrences")
                for q in questions[:3]:
                    print(f"  - {q}")

        print("\n" + "="*70)


def run_test(workflow, question, thread_id):
    """Run a single test case."""
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

    config = {"configurable": {"thread_id": thread_id}}

    start_time = time.time()
    result = workflow.invoke(initial_state, config)
    duration = time.time() - start_time

    if not result.get("final_report"):
        raise Exception("No final report generated")

    if len(result["final_report"]) < 100:
        raise Exception("Report too short")

    return result, duration


def main():
    print("="*70)
    print("MULTI-AGENT RESEARCH ASSISTANT - TEST SUITE")
    print("="*70)
    print(f"\nRunning {len(TEST_QUESTIONS)} test cases...\n")

    workflow = create_workflow()
    results = TestResults()

    for idx, question in enumerate(TEST_QUESTIONS, 1):
        print(f"\nTest {idx}/{len(TEST_QUESTIONS)}: {question}")

        try:
            result, duration = run_test(workflow, question, f"test-{idx}")
            results.add_pass(question, duration)

        except Exception as e:
            duration = 0
            results.add_fail(question, str(e), duration)

    results.print_summary()


if __name__ == "__main__":
    main()
