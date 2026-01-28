from langchain.agents import create_agent
from config import get_llm, get_memory


def create_pro_agent(debug=False):
    """Agent that argues for a position."""
    llm = get_llm()
    memory = get_memory()
    tools = []

    agent = create_agent(llm, tools, checkpointer=memory, debug=debug, system_prompt="""You are a Pro debate agent. Your role is to argue FOR the given position.

Present 3-5 strong arguments supporting the position with evidence and reasoning. Be persuasive but fair.""")

    return agent, memory


def create_con_agent(debug=False):
    """Agent that argues against a position."""
    llm = get_llm()
    memory = get_memory()
    tools = []

    agent = create_agent(llm, tools, checkpointer=memory, debug=debug, system_prompt="""You are a Con debate agent. Your role is to argue AGAINST the given position.

Present 3-5 strong counter-arguments with evidence and reasoning. Be persuasive but fair.""")

    return agent, memory


def create_judge_agent(debug=False):
    """Agent that evaluates debate arguments."""
    llm = get_llm()
    memory = get_memory()
    tools = []

    agent = create_agent(llm, tools, checkpointer=memory, debug=debug, system_prompt="""You are a Judge agent. Evaluate debate arguments objectively.

Assess:
1. Strength of reasoning
2. Quality of evidence
3. Persuasiveness
4. Logical consistency

Provide balanced verdict with scoring.""")

    return agent, memory
