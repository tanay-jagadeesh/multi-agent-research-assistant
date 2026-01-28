import streamlit as st
import time
from workflow import create_workflow
from config import setup_logging
from utils.logging_system import performance_tracker

setup_logging()

st.set_page_config(page_title="Research Assistant", layout="wide")

st.title("🔬 Multi-Agent Research Assistant")
st.markdown("Powered by 6 specialized AI agents working together")

if "workflow" not in st.session_state:
    st.session_state.workflow = create_workflow()
    st.session_state.results = None
    st.session_state.running = False

query = st.text_area(
    "Enter your research question:",
    height=100,
    placeholder="e.g., What is the future of Artificial Intelligence in Healthcare?"
)

col1, col2 = st.columns([1, 4])

with col1:
    start_button = st.button("🚀 Start Research", disabled=st.session_state.running, use_container_width=True)

if start_button and query:
    st.session_state.running = True
    st.session_state.results = None

    progress_container = st.container()

    with progress_container:
        st.markdown("### 📊 Research Progress")

        progress_bar = st.progress(0)
        status_text = st.empty()

        agent_stages = [
            ("Planner", "Breaking down your question..."),
            ("Researcher", "Gathering information from sources..."),
            ("Fact-Checker", "Verifying claims..."),
            ("Citation", "Formatting citations..."),
            ("Analyst", "Synthesizing report..."),
            ("Quality Control", "Evaluating quality...")
        ]

        for idx, (agent, status) in enumerate(agent_stages):
            progress = (idx + 1) / len(agent_stages)
            progress_bar.progress(progress)
            status_text.markdown(f"**Current Agent:** {agent}  \n_{status}_")
            time.sleep(0.5)

        initial_state = {
            "user_query": query,
            "research_plan": None,
            "findings": None,
            "fact_check": None,
            "citations": None,
            "final_report": None,
            "quality_check": None,
            "revision_count": 0,
            "shared_context": None
        }

        config = {"configurable": {"thread_id": f"streamlit-{time.time()}"}}

        try:
            result = st.session_state.workflow.invoke(initial_state, config)
            st.session_state.results = result
            progress_bar.progress(1.0)
            status_text.markdown("**✅ Research Complete!**")

        except Exception as e:
            st.error(f"Error during research: {str(e)}")

    st.session_state.running = False

if st.session_state.results:
    result = st.session_state.results

    st.markdown("---")
    st.markdown("## 📄 Final Report")

    with st.expander("📊 Executive Summary & Analysis", expanded=True):
        st.markdown(result["final_report"])

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📥 Download as Markdown"):
            st.download_button(
                label="Download MD",
                data=result["final_report"],
                file_name="research_report.md",
                mime="text/markdown"
            )

    with col2:
        if st.button("📥 Download as PDF"):
            st.info("PDF export coming soon!")

    with st.expander("🔍 Research Details"):
        tab1, tab2, tab3, tab4 = st.tabs(["Research Plan", "Findings", "Fact-Check", "Quality Score"])

        with tab1:
            st.markdown("### Research Questions")
            st.markdown(result.get("research_plan", "N/A"))

        with tab2:
            st.markdown("### Research Findings")
            st.markdown(result.get("findings", "N/A"))

        with tab3:
            st.markdown("### Fact-Check Results")
            st.markdown(result.get("fact_check", "N/A"))

        with tab4:
            st.markdown("### Quality Evaluation")
            st.markdown(result.get("quality_check", "N/A"))

st.sidebar.markdown("### About")
st.sidebar.markdown("""
This research assistant uses 6 specialized agents:

1. **Planner** - Breaks down questions
2. **Researcher** - Gathers information
3. **Fact-Checker** - Verifies claims
4. **Citation** - Formats sources
5. **Analyst** - Synthesizes report
6. **Quality Control** - Ensures standards

The system includes error handling, retry logic, and quality feedback loops.
""")
