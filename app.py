import queue
import re
import threading
import time
from datetime import datetime

import streamlit as st

from config import setup_logging
from utils.logging_system import performance_tracker
from workflow import create_workflow, set_progress_queue

setup_logging()

st.set_page_config(page_title="Lumern – Research Assistant", layout="wide", page_icon="🔬")

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
.agent-row { display:flex; align-items:center; gap:12px; padding:8px 0; }
.agent-icon { font-size:20px; width:28px; text-align:center; }
.agent-name { font-weight:600; min-width:130px; }
.agent-status { color:#888; font-size:0.85em; }
.agent-time  { margin-left:auto; color:#aaa; font-size:0.8em; font-family:monospace; }
.arrow-down  { text-align:center; color:#444; font-size:18px; line-height:1; margin:-2px 0; }
.pipeline-box{ background:#0e1117; border:1px solid #2a2a2a; border-radius:10px;
               padding:16px 20px; margin-bottom:1rem; }
.qs-badge { display:inline-block; padding:4px 14px; border-radius:20px;
            font-weight:700; font-size:1.1em; }
.qs-pass  { background:#1a3a1a; color:#4caf50; }
.qs-revise{ background:#3a2a0a; color:#ff9800; }
</style>
""", unsafe_allow_html=True)

# ── Session state ────────────────────────────────────────────────────────────
def _init_session():
    if "workflow" not in st.session_state:
        st.session_state.workflow   = create_workflow()
        st.session_state.results    = None
        st.session_state.running    = False
        st.session_state.history    = []  # list of {query, report, score, ts}

_init_session()

# ── Supabase helper (graceful no-op when not configured) ─────────────────────
def _get_supabase():
    try:
        import os
        from supabase import create_client
        url = os.environ.get("SUPABASE_URL", "")
        key = os.environ.get("SUPABASE_ANON_KEY", "")
        if url and key:
            return create_client(url, key)
    except Exception:
        pass
    return None

def _save_to_supabase(query: str, report: str, score: int):
    client = _get_supabase()
    if client is None:
        return
    try:
        client.table("research_history").insert({
            "query": query,
            "report": report,
            "quality_score": score,
            "created_at": datetime.utcnow().isoformat(),
        }).execute()
    except Exception:
        pass

def _load_from_supabase():
    client = _get_supabase()
    if client is None:
        return []
    try:
        res = client.table("research_history") \
                    .select("id, query, quality_score, created_at") \
                    .order("created_at", desc=True).limit(20).execute()
        return res.data or []
    except Exception:
        return []

# ── PDF export ───────────────────────────────────────────────────────────────
def _report_to_pdf(report_text: str, query: str) -> bytes:
    from fpdf import FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Title
    pdf.set_font("Helvetica", "B", 16)
    pdf.multi_cell(0, 10, "Lumern Research Report", align="C")
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(120, 120, 120)
    pdf.multi_cell(0, 7, f"Query: {query}", align="C")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(6)

    # Body — strip markdown symbols for clean PDF output
    clean = re.sub(r"#{1,6}\s*", "", report_text)   # headings
    clean = re.sub(r"\*\*(.*?)\*\*", r"\1", clean)   # bold
    clean = re.sub(r"\*(.*?)\*",   r"\1", clean)     # italic
    clean = re.sub(r"`(.*?)`",     r"\1", clean)     # inline code
    clean = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", clean)  # links → text

    pdf.set_font("Helvetica", "", 10)
    for line in clean.split("\n"):
        line = line.strip()
        if not line:
            pdf.ln(3)
            continue
        try:
            pdf.multi_cell(0, 6, line)
        except Exception:
            pdf.multi_cell(0, 6, line.encode("latin-1", "replace").decode("latin-1"))

    return pdf.output()

# ── Citation link renderer ───────────────────────────────────────────────────
def _render_report_with_links(report_text: str) -> str:
    """Turns [n] inline refs and bare URLs into clickable markdown links."""
    # Extract bibliography lines like: 1. Title (https://...)
    bib_pattern = re.compile(
        r"^\s*(\d+)\.\s+(.+?)\s+\((https?://[^\)]+)\)",
        re.MULTILINE
    )
    url_map: dict[str, str] = {}
    for m in bib_pattern.finditer(report_text):
        num, title, url = m.group(1), m.group(2).strip(), m.group(3).strip()
        url_map[num] = (title, url)

    # Replace [n] inline refs with hyperlinks
    def replace_inline(m):
        n = m.group(1)
        if n in url_map:
            title, url = url_map[n]
            return f"[[{n}]]({url})"
        return m.group(0)

    report_text = re.sub(r"\[(\d+)\](?!\()", replace_inline, report_text)

    # Make bare URLs in bibliography lines clickable
    def replace_bib(m):
        num, title, url = m.group(1), m.group(2).strip(), m.group(3).strip()
        return f"{num}. [{title}]({url})"

    report_text = bib_pattern.sub(replace_bib, report_text)
    return report_text

# ── Pipeline progress UI ─────────────────────────────────────────────────────
AGENTS = [
    ("Planner",         "Breaking down your question"),
    ("Researcher",      "Gathering sources"),
    ("Fact-Checker",    "Verifying claims"),
    ("Citation",        "Formatting citations"),
    ("Analyst",         "Synthesizing report"),
    ("Quality Control", "Evaluating quality"),
]

ICONS = {
    "waiting": "⏳",
    "running": "🔄",
    "done":    "✅",
    "error":   "❌",
}

def _render_pipeline(agent_states: dict):
    html_parts = ['<div class="pipeline-box">']
    for i, (name, subtitle) in enumerate(AGENTS):
        st8 = agent_states.get(name, "waiting")
        icon = ICONS[st8]
        elapsed = agent_states.get(f"{name}_elapsed", None)
        time_str = f"{elapsed:.1f}s" if elapsed else ""

        color = {"waiting": "#555", "running": "#f0a500", "done": "#4caf50", "error": "#f44"}.get(st8, "#555")
        name_style = f"color:{color}" if st8 != "waiting" else "color:#555"

        html_parts.append(
            f'<div class="agent-row">'
            f'  <span class="agent-icon">{icon}</span>'
            f'  <span class="agent-name" style="{name_style}">{name}</span>'
            f'  <span class="agent-status">{subtitle if st8 == "running" else ("" if st8 == "waiting" else "complete")}</span>'
            f'  <span class="agent-time">{time_str}</span>'
            f'</div>'
        )
        if i < len(AGENTS) - 1:
            arrow_color = "#4caf50" if st8 == "done" else "#333"
            html_parts.append(f'<div class="arrow-down" style="color:{arrow_color}">↓</div>')
    html_parts.append('</div>')
    return "\n".join(html_parts)

# ── Extract quality score ────────────────────────────────────────────────────
def _parse_score(quality_check: str) -> int:
    m = re.search(r"(\d{1,3})\s*/\s*100", quality_check or "")
    return int(m.group(1)) if m else 0

# ── Sidebar: history ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🕑 Research History")
    db_history = _load_from_supabase()
    combined = db_history if db_history else st.session_state.history

    if not combined:
        st.caption("No past reports yet.")
    else:
        for item in combined:
            q   = item.get("query", "Unknown query")
            sc  = item.get("quality_score", item.get("score", "?"))
            ts  = item.get("created_at", item.get("ts", ""))[:10] if item.get("created_at") or item.get("ts") else ""
            label = f"**{q[:45]}{'…' if len(q) > 45 else ''}**"
            with st.expander(f"{ts}  score:{sc}", expanded=False):
                st.markdown(label)
                if "report" in item:
                    if st.button("Load report", key=f"load_{ts}_{sc}"):
                        st.session_state.results = {"final_report": item["report"],
                                                     "quality_check": f"Quality Score: {sc}/100"}

    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
**6-agent pipeline:**
1. Planner — decomposes question
2. Researcher — web search & scrape
3. Fact-Checker — verifies claims
4. Citation — formats bibliography
5. Analyst — synthesizes report
6. Quality Control — scores & revises
""")

# ── Main UI ──────────────────────────────────────────────────────────────────
st.title("🔬 Lumern Research Assistant")
st.markdown("Powered by a 6-agent AI pipeline · Verified · Cited · Quality-scored")

query = st.text_area(
    "Enter your research question:",
    height=90,
    placeholder="e.g., What is the future of AI in healthcare?",
    disabled=st.session_state.running,
)

start_button = st.button(
    "🚀 Generate Report",
    disabled=st.session_state.running or not (query or "").strip(),
    use_container_width=False,
)

# ── Run workflow ──────────────────────────────────────────────────────────────
if start_button and query.strip():
    st.session_state.running = True
    st.session_state.results = None

    progress_q: queue.Queue = queue.Queue()
    set_progress_queue(progress_q)

    initial_state = {
        "user_query": query,
        "research_plan": None,
        "findings": None,
        "fact_check": None,
        "citations": None,
        "final_report": None,
        "quality_check": None,
        "revision_count": 0,
        "shared_context": None,
    }
    config = {"configurable": {"thread_id": f"st-{time.time()}"}}
    result_holder: dict = {}

    def _run():
        try:
            result_holder["result"] = st.session_state.workflow.invoke(initial_state, config)
        except Exception as e:
            result_holder["error"] = str(e)
        finally:
            progress_q.put({"agent": "__done__", "status": "done", "elapsed": 0})

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()

    # Live pipeline display
    pipeline_placeholder = st.empty()
    agent_states: dict = {name: "waiting" for name, _ in AGENTS}

    while True:
        try:
            msg = progress_q.get(timeout=0.3)
        except queue.Empty:
            pipeline_placeholder.markdown(
                _render_pipeline(agent_states), unsafe_allow_html=True
            )
            continue

        if msg["agent"] == "__done__":
            break

        name, status, elapsed = msg["agent"], msg["status"], msg["elapsed"]
        agent_states[name] = status
        if elapsed:
            agent_states[f"{name}_elapsed"] = elapsed
        pipeline_placeholder.markdown(
            _render_pipeline(agent_states), unsafe_allow_html=True
        )

    thread.join()

    # Final render — mark all done
    for name, _ in AGENTS:
        if agent_states.get(name) not in ("done", "error"):
            agent_states[name] = "done"
    pipeline_placeholder.markdown(_render_pipeline(agent_states), unsafe_allow_html=True)

    if "error" in result_holder:
        st.error(f"Pipeline error: {result_holder['error']}")
    else:
        result = result_holder.get("result", {})
        st.session_state.results = result
        score = _parse_score(result.get("quality_check", ""))

        # Persist to Supabase + local history
        _save_to_supabase(query, result.get("final_report", ""), score)
        st.session_state.history.insert(0, {
            "query": query,
            "report": result.get("final_report", ""),
            "score": score,
            "ts": datetime.utcnow().isoformat(),
        })

    set_progress_queue(None)
    st.session_state.running = False

# ── Report display ────────────────────────────────────────────────────────────
if st.session_state.results:
    result = st.session_state.results
    report  = result.get("final_report", "")
    qcheck  = result.get("quality_check", "")
    score   = _parse_score(qcheck)

    st.markdown("---")

    # Quality score badge
    badge_cls = "qs-pass" if score >= 70 else "qs-revise"
    st.markdown(
        f'<span class="qs-badge {badge_cls}">Quality Score: {score}/100</span>',
        unsafe_allow_html=True,
    )

    st.markdown("## 📄 Research Report")

    report_with_links = _render_report_with_links(report)
    st.markdown(report_with_links)

    # Export buttons
    col_md, col_pdf, _ = st.columns([1, 1, 4])
    with col_md:
        st.download_button(
            label="⬇ Download Markdown",
            data=report,
            file_name="lumern_report.md",
            mime="text/markdown",
        )
    with col_pdf:
        try:
            pdf_bytes = _report_to_pdf(report, query or "")
            st.download_button(
                label="⬇ Download PDF",
                data=bytes(pdf_bytes),
                file_name="lumern_report.pdf",
                mime="application/pdf",
            )
        except ImportError:
            st.info("Install fpdf2 for PDF export: `pip install fpdf2`")

    # Details expander
    with st.expander("🔍 Pipeline Details"):
        tab1, tab2, tab3, tab4 = st.tabs(["Research Plan", "Findings", "Fact-Check", "Quality Score"])
        with tab1:
            st.markdown(result.get("research_plan") or "_Not available_")
        with tab2:
            st.markdown(result.get("findings") or "_Not available_")
        with tab3:
            st.markdown(result.get("fact_check") or "_Not available_")
        with tab4:
            st.markdown(qcheck or "_Not available_")
