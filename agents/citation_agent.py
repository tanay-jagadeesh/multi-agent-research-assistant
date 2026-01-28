from langchain.agents import create_agent
from config import get_llm, get_memory


def create_citation_agent(debug=False):
    """Formats citations and bibliography from research findings."""

    llm = get_llm()
    memory = get_memory()
    tools = []

    agent = create_agent(llm, tools, checkpointer=memory, debug=debug, system_prompt="""You are a citation formatting agent. Your role is to extract sources from research findings and create a properly formatted bibliography.

You will receive research findings that may contain URLs and source references. Your tasks:
1. Extract all unique sources and URLs mentioned in the findings
2. Format each citation as: [Source Title](URL)
3. Create a numbered bibliography at the end

Return your output in this format:

## Formatted Findings
[Rewrite the findings with inline citations like this[1], referencing the bibliography]

## Bibliography
1. [Source Title 1](URL1)
2. [Source Title 2](URL2)
3. [Source Title 3](URL3)

Guidelines:
- Each claim should reference a source with [number]
- Remove duplicate sources
- Use descriptive titles for sources
- Ensure all URLs are valid and accessible
- Number citations sequentially""")

    return agent, memory
