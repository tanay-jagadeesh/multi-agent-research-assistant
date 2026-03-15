<div align="center">

# Multi-Agent Research Assistant

### Autonomous research powered by a coordinated team of AI agents

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.0-green.svg)](https://github.com/langchain-ai/langgraph)
[![LangChain](https://img.shields.io/badge/LangChain-1.2-orange.svg)](https://github.com/langchain-ai/langchain)
[![Streamlit](https://img.shields.io/badge/Streamlit-UI-red.svg)](https://streamlit.io/)

*Ask a complex question. Get a verified, cited, quality-checked research report.*

</div>

---

## The Problem

Research is time-consuming. You ask a question, open a dozen tabs, cross-reference sources, verify claims, organize findings, and write it all up. What if a team of specialized AI agents could do that for you — and check each other's work?

## The Solution

This system orchestrates **6 specialized agents** through a stateful pipeline that mirrors how a real research team operates:

```
Question → Plan → Research → Verify → Cite → Analyze → QC → Report
```

Each agent has a defined role, and the pipeline includes a **quality feedback loop** — if the report doesn't meet standards, it gets sent back for revision automatically.

---

## Architecture

```
                          ┌─────────────┐
                          │   Planner   │  Breaks query into 3-5
                          │    Agent    │  focused sub-questions
                          └──────┬──────┘
                                 │
                          ┌──────▼──────┐
                          │  Research   │  Web search + page scraping
                          │    Agent    │  for each sub-question
                          └──────┬──────┘
                                 │
                          ┌──────▼──────┐
                          │ Fact-Check  │  Verifies key claims with
                          │    Agent    │  independent source checks
                          └──────┬──────┘
                                 │
                          ┌──────▼──────┐
                          │  Citation   │  Extracts & formats sources
                          │    Agent    │  into proper bibliography
                          └──────┬──────┘
                                 │
                          ┌──────▼──────┐
                          │   Analyst   │  Synthesizes everything into
                          │    Agent    │  a structured report
                          └──────┬──────┘
                                 │
                          ┌──────▼──────┐
                     ┌───►│  Quality    │  Scores on 5 criteria
                     │    │  Control    │  (100-point rubric)
                     │    └──────┬──────┘
                     │           │
                     │     ┌─────▼─────┐
                     │     │  Score     │
                     │     │  ≥ 70?    │
                     │     └─────┬─────┘
                     │      No   │   Yes
                     └───────────┘    │
                                 ┌────▼────┐
                                 │  Final  │
                                 │ Report  │
                                 └─────────┘
```

Built with **LangGraph's StateGraph** for deterministic orchestration and shared state across all agents.

---

## Agents

| Agent | Role | Tools | Output |
|-------|------|-------|--------|
| **Planner** | Decomposes complex questions into focused sub-questions | — | 3-5 research sub-questions |
| **Researcher** | Gathers evidence from the web | `web_search`, `fetch_webpage` | Structured findings per sub-question |
| **Fact-Checker** | Independently verifies key claims | `web_search` | Verified / Partially Verified / Unverified / False |
| **Citation** | Extracts and formats all sources | — | Numbered bibliography with inline refs |
| **Analyst** | Synthesizes findings into a report | — | Executive summary, analysis, insights, conclusions |
| **Quality Control** | Evaluates report against a scoring rubric | — | Score (0-100) + actionable feedback |

### Quality Scoring Rubric

| Criteria | Weight |
|----------|--------|
| Structure & Organization | 25 |
| Evidence & Support | 25 |
| Accuracy & Reliability | 25 |
| Comprehensiveness | 15 |
| Clarity & Readability | 10 |

Reports scoring below **70** are automatically sent back to the Analyst with specific feedback (up to 2 revision cycles).

---

## Features

- **End-to-end automation** — from question to polished report with citations
- **Fact verification** — claims are independently checked, not just repeated
- **Quality feedback loop** — reports are scored and revised until they pass
- **Inter-agent communication** — agents share context through a message bus
- **Resilient execution** — automatic retries, graceful fallbacks, error recovery
- **Performance tracking** — execution time, token usage, and cost estimates per agent
- **Dual interfaces** — CLI for scripts, Streamlit for interactive use
- **Persistent memory** — conversation state saved across sessions via LangGraph checkpointing

---

## Quick Start

### Prerequisites

- Python 3.12+
- OpenAI API key

### Installation

```bash
git clone https://github.com/yourusername/multi-agent-research-assistant.git
cd multi-agent-research-assistant

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root:

```
OPENAI_API_KEY=your_api_key_here
```

### Run

**CLI:**
```bash
python main.py
```

**Web UI:**
```bash
streamlit run app.py
```

---

## Project Structure

```
multi-agent-research-assistant/
├── agents/
│   ├── planner_agent.py          # Query decomposition
│   ├── research_agent.py         # Web research & evidence gathering
│   ├── fact_checker_agent.py     # Independent claim verification
│   ├── citation_agent.py         # Source formatting & bibliography
│   ├── analyst_agent.py          # Report synthesis
│   ├── quality_control_agent.py  # Scoring & feedback
│   └── communication.py          # Inter-agent message bus
├── tools/
│   ├── web_search.py             # DuckDuckGo search integration
│   ├── url_fetcher.py            # Webpage content extraction
│   ├── summarizer.py             # LLM-powered summarization
│   └── file_saver.py             # Output persistence
├── config/
│   └── settings.py               # LLM, memory, and logging config
├── utils/
│   ├── error_handling.py         # Retry logic & safe invocation
│   └── logging_system.py         # Performance tracking & metrics
├── state.py                      # Shared ResearchState definition
├── workflow.py                   # LangGraph StateGraph orchestration
├── main.py                       # CLI entry point
├── app.py                        # Streamlit web interface
└── requirements.txt
```

---

## How It Works

```python
# The entire pipeline in 4 lines
from workflow import create_research_workflow

workflow = create_research_workflow()
result = workflow.invoke({"user_query": "What is the future of AI in healthcare?"})
print(result["final_report"])
```

The system will:
1. Break the question into sub-questions
2. Search the web and scrape relevant pages
3. Verify key claims against independent sources
4. Format a proper bibliography
5. Write a structured report with executive summary, analysis, and conclusions
6. Score the report — revise if needed
7. Return the final, quality-checked report

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Orchestration | LangGraph (StateGraph) |
| Agent Framework | LangChain |
| LLM | OpenAI GPT-3.5-turbo |
| Web Search | DuckDuckGo |
| Web Scraping | BeautifulSoup4 |
| State Persistence | LangGraph MemorySaver |
| Web UI | Streamlit |
| Error Handling | Custom retry decorators + tenacity |

---

## Experimental

The repo also includes experimental multi-perspective agents (not in the main pipeline):

- **Debate Agents** — Pro/Con/Judge framework for adversarial analysis
- **Voting Agents** — Parallel researchers with consensus aggregation

---

## License

MIT

---

<div align="center">

Built with LangChain + LangGraph

</div>
