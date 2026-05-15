"""
FastAPI backend for Lumern Research Assistant.
Exposes:
  POST /api/research        — start a research job (returns job_id)
  GET  /api/research/{id}/stream — SSE stream of agent progress + final result
  GET  /api/history         — fetch research history from Supabase
"""
import json
import os
import queue
import threading
import time
import uuid
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

load_dotenv()

from workflow import create_workflow, set_progress_queue

app = FastAPI(title="Lumern API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job store  {job_id: {"queue": Queue, "result": dict|None, "error": str|None}}
_jobs: dict[str, dict] = {}
_workflow = None

def _get_workflow():
    global _workflow
    if _workflow is None:
        _workflow = create_workflow()
    return _workflow


# ── Supabase helpers ──────────────────────────────────────────────────────────
def _get_supabase():
    try:
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
    if not client:
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
    if not client:
        return []
    try:
        res = (client.table("research_history")
               .select("id, query, quality_score, created_at")
               .order("created_at", desc=True)
               .limit(30)
               .execute())
        return res.data or []
    except Exception:
        return []


# ── Score extractor ────────────────────────────────────────────────────────────
import re

def _parse_score(quality_check: str) -> int:
    m = re.search(r"(\d{1,3})\s*/\s*100", quality_check or "")
    return int(m.group(1)) if m else 0


# ── Request / Response models ──────────────────────────────────────────────────
class ResearchRequest(BaseModel):
    query: str

class JobCreated(BaseModel):
    job_id: str


# ── Endpoints ──────────────────────────────────────────────────────────────────
@app.post("/api/research", response_model=JobCreated)
def start_research(body: ResearchRequest):
    job_id = str(uuid.uuid4())
    q: queue.Queue = queue.Queue()
    _jobs[job_id] = {"queue": q, "result": None, "error": None}

    def _run():
        wf = _get_workflow()
        set_progress_queue(q)
        initial_state = {
            "user_query": body.query,
            "research_plan": None,
            "findings": None,
            "fact_check": None,
            "citations": None,
            "final_report": None,
            "quality_check": None,
            "revision_count": 0,
            "shared_context": None,
        }
        config = {"configurable": {"thread_id": f"api-{job_id}"}}
        try:
            result = wf.invoke(initial_state, config)
            _jobs[job_id]["result"] = result
            score = _parse_score(result.get("quality_check", ""))
            _save_to_supabase(body.query, result.get("final_report", ""), score)
        except Exception as e:
            _jobs[job_id]["error"] = str(e)
        finally:
            set_progress_queue(None)
            q.put({"agent": "__done__", "status": "done", "elapsed": 0})

    threading.Thread(target=_run, daemon=True).start()
    return JobCreated(job_id=job_id)


@app.get("/api/research/{job_id}/stream")
def stream_research(job_id: str):
    if job_id not in _jobs:
        return {"error": "job not found"}

    def _generate():
        job = _jobs[job_id]
        q   = job["queue"]

        while True:
            try:
                msg = q.get(timeout=30)
            except queue.Empty:
                # Send keepalive
                yield f"data: {json.dumps({'type': 'keepalive'})}\n\n"
                continue

            if msg["agent"] == "__done__":
                result = job.get("result")
                error  = job.get("error")
                if error:
                    yield f"data: {json.dumps({'type': 'error', 'message': error})}\n\n"
                else:
                    score = _parse_score(result.get("quality_check", ""))
                    payload = {
                        "type": "result",
                        "final_report":   result.get("final_report", ""),
                        "research_plan":  result.get("research_plan", ""),
                        "findings":       result.get("findings", ""),
                        "fact_check":     result.get("fact_check", ""),
                        "citations":      result.get("citations", ""),
                        "quality_check":  result.get("quality_check", ""),
                        "quality_score":  score,
                        "revision_count": result.get("revision_count", 0),
                    }
                    yield f"data: {json.dumps(payload)}\n\n"
                # Clean up job after a delay
                threading.Timer(60, lambda: _jobs.pop(job_id, None)).start()
                break
            else:
                yield f"data: {json.dumps({'type': 'progress', **msg})}\n\n"

    return StreamingResponse(
        _generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/api/history")
def get_history():
    return {"history": _load_from_supabase()}


@app.get("/api/health")
def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}
