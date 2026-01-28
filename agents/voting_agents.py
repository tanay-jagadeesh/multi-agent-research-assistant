from langchain.agents import create_agent
from config import get_llm, get_memory
from tools import web_search


def create_parallel_researcher(researcher_id, debug=False):
    """Create a researcher agent for parallel execution."""
    llm = get_llm()
    memory = get_memory()
    tools = [web_search]

    agent = create_agent(llm, tools, checkpointer=memory, debug=debug, system_prompt=f"""You are Researcher {researcher_id}. Conduct independent research on the given topic.

Focus on finding unique perspectives and sources. Return findings in this format:

Researcher {researcher_id} Findings:
- [Key finding 1]
- [Key finding 2]
- [Key finding 3]""")

    return agent, memory


def create_consensus_agent(debug=False):
    """Agent that builds consensus from multiple answers."""
    llm = get_llm()
    memory = get_memory()
    tools = []

    agent = create_agent(llm, tools, checkpointer=memory, debug=debug, system_prompt="""You are a Consensus agent. Compare findings from multiple researchers.

Your tasks:
1. Identify common themes across all findings
2. Note unique insights from each researcher
3. Evaluate evidence quality for each claim
4. Build consensus on best-supported conclusions

Return:

## Consensus Findings
[Points agreed upon by multiple researchers]

## Best Supported Claims
[Claims with strongest evidence]

## Unique Insights
[Notable findings from individual researchers]

## Recommended Conclusion
[Most reliable conclusion based on all evidence]""")

    return agent, memory
