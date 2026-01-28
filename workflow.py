from langgraph.graph import StateGraph, END
from state import ResearchState
from agents.planner_agent import create_planner_agent
from agents.research_agent import create_research_agent
from agents.fact_checker_agent import create_fact_checker_agent
from agents.analyst_agent import create_analyst_agent
from config import get_memory


def planner_node(state: ResearchState) -> ResearchState:
    """Planner agent node: breaks down user query into sub-questions."""
    planner_agent, _ = create_planner_agent()

    config = {"configurable": {"thread_id": "planner-1"}}
    inputs = {"messages": [{"role": "user", "content": state["user_query"]}]}

    result = planner_agent.invoke(inputs, config)
    research_plan = result['messages'][-1].content

    return {"research_plan": research_plan}


def researcher_node(state: ResearchState) -> ResearchState:
    """Research agent node: gathers findings for each sub-question."""
    researcher_agent, _ = create_research_agent()

    config = {"configurable": {"thread_id": "researcher-1"}}
    inputs = {"messages": [{"role": "user", "content": state["research_plan"]}]}

    result = researcher_agent.invoke(inputs, config)
    findings = result['messages'][-1].content

    return {"findings": findings}


def fact_checker_node(state: ResearchState) -> ResearchState:
    """Fact-checker agent node: verifies claims in research findings."""
    fact_checker_agent, _ = create_fact_checker_agent()

    config = {"configurable": {"thread_id": "fact-checker-1"}}
    inputs = {"messages": [{"role": "user", "content": state["findings"]}]}

    result = fact_checker_agent.invoke(inputs, config)
    fact_check = result['messages'][-1].content

    return {"fact_check": fact_check}


def analyst_node(state: ResearchState) -> ResearchState:
    """Analyst agent node: synthesizes findings into final report."""
    analyst_agent, _ = create_analyst_agent()

    config = {"configurable": {"thread_id": "analyst-1"}}

    combined_input = f"Research Findings:\n{state['findings']}\n\nFact-Check Results:\n{state['fact_check']}"
    inputs = {"messages": [{"role": "user", "content": combined_input}]}

    result = analyst_agent.invoke(inputs, config)
    final_report = result['messages'][-1].content

    return {"final_report": final_report}


def create_workflow():
    """Creates the research assistant workflow graph."""
    workflow = StateGraph(ResearchState)

    workflow.add_node("planner", planner_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("fact_checker", fact_checker_node)
    workflow.add_node("analyst", analyst_node)

    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "researcher")
    workflow.add_edge("researcher", "fact_checker")
    workflow.add_edge("fact_checker", "analyst")
    workflow.add_edge("analyst", END)

    memory = get_memory()
    return workflow.compile(checkpointer=memory)
