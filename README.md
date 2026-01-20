# Multi-Agent Research Assistant

A multi-agent research system built with LangChain and LangGraph.

## Project Structure

```
multi-agent-research-assistant/
├── agents/                 # Agent definitions
│   ├── __init__.py
│   └── research_agent.py   # Single research agent (Week 1)
├── config/                 # Configuration and settings
│   ├── __init__.py
│   └── settings.py         # Logging, LLM, and memory setup
├── tools/                  # Custom tools
│   ├── __init__.py
│   ├── web_search.py       # DuckDuckGo search
│   ├── url_fetcher.py      # Webpage content fetcher
│   ├── summarizer.py       # Text summarization
│   └── file_saver.py       # Save results to file
├── output/                 # Generated output files
├── main.py                 # Main entry point
├── agentic.py             # Original single-file version (deprecated)
├── .env                    # Environment variables
└── README.md
```

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install langchain langchain-openai langchain-community langgraph python-dotenv requests beautifulsoup4 duckduckgo-search
```

3. Create `.env` file:
```
OPENAI_API_KEY=your_api_key_here
```

## Usage

Run the research assistant:
```bash
python main.py
```

Or import and use in your own code:
```python
from config import setup_logging
from agents import create_research_agent

setup_logging()
agent, memory = create_research_agent(debug=True)

config = {"configurable": {"thread_id": "my-session"}}
inputs = {"messages": [{"role": "user", "content": "Your query here"}]}
result = agent.invoke(inputs, config)
```

## Available Tools

- **Wikipedia**: Look up factual information
- **LLM-Math**: Perform mathematical calculations
- **Web Search**: Search current web information via DuckDuckGo
- **Fetch Webpage**: Extract text content from URLs
- **Summarize**: Summarize long text content
- **File Saver**: Save results to files in the output/ directory

## Next Steps (Week 2+)

When you're ready to add multi-agent capabilities:

1. Add new agents to `agents/` directory:
   - `planner_agent.py` - Breaks down complex questions
   - `searcher_agent.py` - Specialized web searching
   - `analyst_agent.py` - Synthesizes findings

2. Create state management in new `state/` directory

3. Build orchestration logic to coordinate agents

## Development

The refactored structure makes it easy to:
- Add new tools in `tools/` directory
- Add new agents in `agents/` directory
- Modify configuration in `config/`
- Keep main logic clean and organized
