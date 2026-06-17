"""
Benchmark script for the multi-agent research pipeline.
Measures latency, token throughput, and end-to-end pipeline timing.
"""
import time
import statistics
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from workflow import (
    planner_node, researcher_node, fact_checker_node,
    citation_node, analyst_node, quality_control_node
)

# ─── test inputs ──────────────────────────────────────────────────────────────
QUERY = "What are the latest advancements in large language models in 2024?"

MOCK_PLAN = """1. What new LLM architectures were released in 2024?
2. How have context window sizes improved in 2024 LLMs?
3. What are the benchmark performance improvements of 2024 LLMs?"""

MOCK_FINDINGS = """Question 1: What new LLM architectures were released in 2024?
Findings:
- GPT-4o introduced multimodal capabilities combining text, audio, and vision (Source: https://openai.com/blog/gpt-4o)
- Google released Gemini 1.5 Pro with a 1M token context window (Source: https://blog.google/technology/ai/google-gemini-next-generation-model-february-2024)
- Meta released Llama 3 with improved instruction following (Source: https://ai.meta.com/blog/meta-llama-3)

Question 2: How have context window sizes improved in 2024 LLMs?
Findings:
- Gemini 1.5 Pro supports up to 1 million tokens (Source: https://blog.google/technology/ai/google-gemini-next-generation-model-february-2024)
- Claude 3 supports 200k token context windows (Source: https://www.anthropic.com/news/claude-3-family)
- GPT-4 Turbo supports 128k token context (Source: https://openai.com/blog/new-models-and-developer-products-announced-at-devday)

Question 3: What are the benchmark performance improvements of 2024 LLMs?
Findings:
- Claude 3 Opus scores 86.8% on MMLU benchmark (Source: https://www.anthropic.com/news/claude-3-family)
- Gemini Ultra achieves 90.0% on MMLU, surpassing human expert performance (Source: https://blog.google/technology/ai/google-gemini-ai)
- GPT-4o matches GPT-4 Turbo performance at twice the speed (Source: https://openai.com/blog/gpt-4o)"""

MOCK_FACT_CHECK = """Claim 1: GPT-4o introduced multimodal capabilities
Status: Verified
Evidence: Confirmed by OpenAI's official announcement in May 2024.

Claim 2: Gemini 1.5 Pro supports 1M token context
Status: Verified
Evidence: Google confirmed this in their February 2024 announcement.

Claim 3: Claude 3 Opus scores 86.8% on MMLU
Status: Verified
Evidence: Anthropic's model card confirms this benchmark score."""

MOCK_CITATIONS = """## Formatted Findings
- GPT-4o introduced multimodal capabilities [1]
- Gemini 1.5 Pro supports 1M token context [2]
- Meta released Llama 3 [3]

## Bibliography
1. OpenAI Blog – GPT-4o (https://openai.com/blog/gpt-4o)
2. Google Blog – Gemini 1.5 (https://blog.google/technology/ai/google-gemini-next-generation-model-february-2024)
3. Meta AI – Llama 3 (https://ai.meta.com/blog/meta-llama-3)"""

MOCK_REPORT = """# LLM Advancements in 2024

## Executive Summary
2024 saw major leaps in LLM capability, with context windows reaching 1M tokens and multimodal models becoming mainstream.

## Key Findings
- GPT-4o: multimodal, 2x faster than GPT-4 Turbo [1]
- Gemini 1.5 Pro: 1M token context window [2]
- Claude 3 Opus: 86.8% MMLU score [3]

## Conclusion
The 2024 LLM landscape is defined by scale, speed, and multimodality."""

# ─── helpers ──────────────────────────────────────────────────────────────────

def run_agent(fn, state, runs=3):
    """Run an agent node `runs` times, return list of elapsed seconds."""
    times = []
    for _ in range(runs):
        t0 = time.perf_counter()
        fn(state)
        times.append(time.perf_counter() - t0)
    return times

def fmt(times):
    avg = statistics.mean(times)
    mn  = min(times)
    mx  = max(times)
    sd  = statistics.stdev(times) if len(times) > 1 else 0.0
    return avg, mn, mx, sd

# ─── main benchmark ──────────────────────────────────────────────────────────

def main():
    RUNS = 3

    agents = [
        ("Planner",         planner_node,        {"user_query": QUERY}),
        ("Researcher",      researcher_node,     {"research_plan": MOCK_PLAN}),
        ("Fact-Checker",    fact_checker_node,   {"findings": MOCK_FINDINGS}),
        ("Citation",        citation_node,       {"findings": MOCK_FINDINGS}),
        ("Analyst",         analyst_node,        {"findings": MOCK_FINDINGS,
                                                   "fact_check": MOCK_FACT_CHECK,
                                                   "citations": MOCK_CITATIONS,
                                                   "shared_context": "",
                                                   "quality_check": "",
                                                   "revision_count": 0}),
        ("Quality Control", quality_control_node, {"final_report": MOCK_REPORT,
                                                    "fact_check": MOCK_FACT_CHECK,
                                                    "citations": MOCK_CITATIONS}),
    ]

    print("\n" + "=" * 70)
    print("  MULTI-AGENT RESEARCH PIPELINE  —  BENCHMARK RESULTS")
    print(f"  {RUNS} runs per agent  |  Model: gpt-3.5-turbo")
    print("=" * 70)
    print(f"{'Agent':<20} {'Avg (s)':>8} {'Min (s)':>8} {'Max (s)':>8} {'StdDev':>8}")
    print("-" * 70)

    all_times = []
    results = {}

    for name, fn, state in agents:
        print(f"  Benchmarking {name}...", end="", flush=True)
        times = run_agent(fn, state, runs=RUNS)
        avg, mn, mx, sd = fmt(times)
        results[name] = {"avg": avg, "min": mn, "max": mx, "std": sd, "times": times}
        all_times.extend(times)
        print(f"\r{name:<20} {avg:>8.2f} {mn:>8.2f} {mx:>8.2f} {sd:>8.2f}")

    # ── end-to-end pipeline estimate ──────────────────────────────────────────
    # Researcher + Fact-Checker run sequentially; others overlap or are fast.
    # Conservative sequential sum of all agents.
    pipeline_avg = sum(r["avg"] for r in results.values())

    print("-" * 70)
    print(f"{'E2E Pipeline (est.)':<20} {pipeline_avg:>8.2f}")
    print("=" * 70)

    # ── resume-friendly summary ────────────────────────────────────────────────
    print("\n  RESUME-READY METRICS\n")
    for name, r in results.items():
        print(f"  • {name} agent: avg {r['avg']:.1f}s  (range {r['min']:.1f}–{r['max']:.1f}s)")
    print(f"\n  • Full 6-agent pipeline completes in ~{pipeline_avg:.0f}s end-to-end")
    fast = min(results, key=lambda n: results[n]["avg"])
    slow = max(results, key=lambda n: results[n]["avg"])
    print(f"  • Fastest agent: {fast} ({results[fast]['avg']:.1f}s avg)")
    print(f"  • Slowest agent: {slow} ({results[slow]['avg']:.1f}s avg)")
    print()

if __name__ == "__main__":
    main()
