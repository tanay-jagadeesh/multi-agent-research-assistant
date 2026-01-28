from langgraph.graph import StateGraph, END
from state import ResearchState
from agents.planner_agent import create_planner_agent
from agents.research_agent import create_research_agent
from agents.fact_checker_agent import create_fact_checker_agent
from agents.citation_agent import create_citation_agent
from agents.analyst_agent import create_analyst_agent
from agents.quality_control_agent import create_quality_control_agent
from config import get_memory


def planner_node(state: ResearchState) -> ResearchState:
    """Planner agent node: breaks down user query into sub-questions."""
    from utils.error_handling import safe_agent_invoke, validate_state_field, retry_on_failure
    from utils.logging_system import log_agent_action

    @log_agent_action("Planner")
    @retry_on_failure(max_retries=3)
    def invoke_planner():
        planner_agent, _ = create_planner_agent()
        config = {"configurable": {"thread_id": "planner-1"}}

        user_query = validate_state_field(state, "user_query", "No query provided")
        inputs = {"messages": [{"role": "user", "content": user_query}]}

        result = safe_agent_invoke(planner_agent, inputs, config, "Planner")
        if result is None:
            raise Exception("Planner agent failed to return results")

        return result['messages'][-1].content

    try:
        research_plan = invoke_planner()
        return {"research_plan": research_plan}
    except Exception as e:
        return {"research_plan": f"Error in planning: {str(e)}. Using single question approach: {state.get('user_query', '')}"}


def researcher_node(state: ResearchState) -> ResearchState:
    """Research agent node: gathers findings for each sub-question."""
    from utils.error_handling import safe_agent_invoke, validate_state_field, retry_on_failure
    from utils.logging_system import log_agent_action

    @log_agent_action("Researcher")
    @retry_on_failure(max_retries=3)
    def invoke_researcher():
        researcher_agent, _ = create_research_agent()
        config = {"configurable": {"thread_id": "researcher-1"}}

        research_plan = validate_state_field(state, "research_plan", "No research plan available")
        inputs = {"messages": [{"role": "user", "content": research_plan}]}

        result = safe_agent_invoke(researcher_agent, inputs, config, "Researcher")
        if result is None:
            raise Exception("Researcher agent failed to return results")

        return result['messages'][-1].content

    try:
        findings = invoke_researcher()
        return {"findings": findings}
    except Exception as e:
        return {"findings": f"Error in research: {str(e)}. Using fallback data."}


def fact_checker_node(state: ResearchState) -> ResearchState:
    """Fact-checker agent node: verifies claims in research findings."""
    fact_checker_agent, _ = create_fact_checker_agent()

    config = {"configurable": {"thread_id": "fact-checker-1"}}
    inputs = {"messages": [{"role": "user", "content": state["findings"]}]}

    result = fact_checker_agent.invoke(inputs, config)
    fact_check = result['messages'][-1].content

    return {"fact_check": fact_check}


def citation_node(state: ResearchState) -> ResearchState:
    """Citation agent node: formats citations and bibliography."""
    citation_agent, _ = create_citation_agent()

    config = {"configurable": {"thread_id": "citation-1"}}
    inputs = {"messages": [{"role": "user", "content": state["findings"]}]}

    result = citation_agent.invoke(inputs, config)
    citations = result['messages'][-1].content

    return {"citations": citations}


def analyst_node(state: ResearchState) -> ResearchState:
    """Analyst agent node: synthesizes findings into final report."""
    from agents.communication import add_agent_message

    analyst_agent, _ = create_analyst_agent()

    config = {"configurable": {"thread_id": "analyst-1"}}

    combined_input = f"Research Findings:\n{state['findings']}\n\nFact-Check Results:\n{state['fact_check']}\n\nCitations:\n{state['citations']}"

    shared_context = state.get("shared_context", "")
    if shared_context:
        combined_input += f"\n\nShared Context:\n{shared_context}"

    if state.get("quality_check"):
        combined_input += f"\n\nPrevious Quality Feedback:\n{state['quality_check']}\n\nPlease revise the report based on this feedback."

    inputs = {"messages": [{"role": "user", "content": combined_input}]}

    result = analyst_agent.invoke(inputs, config)
    final_report = result['messages'][-1].content

    updated_context = add_agent_message(state, "Analyst", "Completed report synthesis")

    revision_count = state.get("revision_count", 0)
    return {"final_report": final_report, "revision_count": revision_count + 1, "shared_context": updated_context}


def quality_control_node(state: ResearchState) -> ResearchState:
    """Quality control agent node: evaluates report quality."""
    qc_agent, _ = create_quality_control_agent()

    config = {"configurable": {"thread_id": "qc-1"}}

    combined_input = f"Final Report:\n{state['final_report']}\n\nFact-Check Results:\n{state['fact_check']}\n\nCitations:\n{state['citations']}"
    inputs = {"messages": [{"role": "user", "content": combined_input}]}

    result = qc_agent.invoke(inputs, config)
    quality_check = result['messages'][-1].content

    return {"quality_check": quality_check}


def should_revise(state: ResearchState) -> str:
    """Decision function: check if report needs revision."""
    quality_check = state.get("quality_check", "")
    revision_count = state.get("revision_count", 0)

    if revision_count >= 2:
        return "end"

    if "Decision: REVISE" in quality_check or "REVISE" in quality_check:
        return "revise"

    return "end"


def create_workflow():
    """Creates the research assistant workflow graph."""
    workflow = StateGraph(ResearchState)

    workflow.add_node("planner", planner_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("fact_checker", fact_checker_node)
    workflow.add_node("citation", citation_node)
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("quality_control", quality_control_node)

    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "researcher")
    workflow.add_edge("researcher", "fact_checker")
    workflow.add_edge("fact_checker", "citation")
    workflow.add_edge("citation", "analyst")
    workflow.add_edge("analyst", "quality_control")

    workflow.add_conditional_edges(
        "quality_control",
        should_revise,
        {
            "revise": "analyst",
            "end": END
        }
    )

    memory = get_memory()
    return workflow.compile(checkpointer=memory)
