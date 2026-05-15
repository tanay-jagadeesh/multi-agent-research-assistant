"use client";

import { useState, useRef, useCallback } from "react";
import Sidebar from "@/components/Sidebar";
import Pipeline from "@/components/Pipeline";
import ReportView from "@/components/ReportView";
import { startResearch, streamResearch } from "@/lib/api";
import type { AgentState, AgentStatus, ResearchResult } from "@/lib/types";

const AGENT_NAMES = ["Planner", "Researcher", "Fact-Checker", "Citation", "Analyst", "Quality Control"];

const EXAMPLE_QUERIES = [
  "What is the future of AI in healthcare?",
  "How does quantum computing threaten current encryption?",
  "What are the geopolitical implications of Arctic resource competition?",
];

function initAgents(): Record<string, AgentState> {
  return Object.fromEntries(AGENT_NAMES.map((n) => [n, { name: n, status: "waiting" }]));
}

export default function Home() {
  const [query, setQuery] = useState("");
  const [running, setRunning] = useState(false);
  const [agents, setAgents] = useState<Record<string, AgentState>>(initAgents());
  const [result, setResult] = useState<ResearchResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const stopRef = useRef<(() => void) | null>(null);

  const updateAgent = useCallback((name: string, status: AgentStatus, elapsed?: number) => {
    setAgents((prev) => ({
      ...prev,
      [name]: { name, status, elapsed: elapsed ?? prev[name]?.elapsed },
    }));
  }, []);

  async function handleSubmit(e: React.FormEvent | null, overrideQuery?: string) {
    e?.preventDefault();
    const q = (overrideQuery ?? query).trim();
    if (!q || running) return;

    setRunning(true);
    setError(null);
    setResult(null);
    setAgents(initAgents());
    if (overrideQuery) setQuery(overrideQuery);

    try {
      const jobId = await startResearch(q);
      const stop = streamResearch(
        jobId,
        (agent, status, elapsed) => {
          updateAgent(agent, status as AgentStatus, elapsed);
        },
        (res) => {
          setResult(res);
          // Mark all done in case of fast completion
          setAgents((prev) => {
            const next = { ...prev };
            for (const n of AGENT_NAMES) {
              if (next[n]?.status !== "done") next[n] = { name: n, status: "done" };
            }
            return next;
          });
          setRunning(false);
        },
        (msg) => {
          setError(msg);
          setRunning(false);
        }
      );
      stopRef.current = stop;
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to connect to API");
      setRunning(false);
    }
  }

  function handleLoadFromHistory(q: string) {
    handleSubmit(null, q);
  }

  return (
    <div style={{ display: "flex", minHeight: "100vh" }}>
      <Sidebar onLoadReport={handleLoadFromHistory} />

      {/* Main */}
      <main style={{ flex: 1, display: "flex", flexDirection: "column", overflowY: "auto" }}>
        {/* Hero / Search */}
        {!result && !running && (
          <div
            style={{
              flex: 1,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              padding: "60px 24px",
            }}
          >
            {/* Badge */}
            <div
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 6,
                background: "var(--accent-dim)",
                border: "1px solid rgba(99,102,241,0.3)",
                borderRadius: 20,
                padding: "4px 14px",
                marginBottom: 28,
              }}
            >
              <span style={{ fontSize: "0.7rem", color: "var(--accent-hover)", fontWeight: 600, letterSpacing: "0.05em" }}>
                POWERED BY 6 AI AGENTS
              </span>
            </div>

            <h1
              style={{
                fontSize: "clamp(2rem, 5vw, 3.2rem)",
                fontWeight: 800,
                textAlign: "center",
                lineHeight: 1.15,
                color: "var(--text-primary)",
                marginBottom: 16,
                maxWidth: 680,
              }}
            >
              Research anything.{" "}
              <span style={{ color: "var(--accent-hover)" }}>Verified.</span>
            </h1>
            <p
              style={{
                color: "var(--text-secondary)",
                fontSize: "1.05rem",
                textAlign: "center",
                maxWidth: 520,
                lineHeight: 1.7,
                marginBottom: 40,
              }}
            >
              Lumern runs a full research pipeline — planning, web research, fact-checking, citations, analysis, and quality control — automatically.
            </p>

            {/* Search form */}
            <form onSubmit={handleSubmit} style={{ width: "100%", maxWidth: 640 }}>
              <div
                style={{
                  display: "flex",
                  alignItems: "flex-end",
                  gap: 10,
                  background: "var(--bg-card)",
                  border: "1px solid var(--border-bright)",
                  borderRadius: 12,
                  padding: 6,
                  transition: "border-color 0.2s",
                }}
                onFocus={() => {}}
              >
                <textarea
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSubmit(null); }
                  }}
                  placeholder="Ask a research question…"
                  rows={2}
                  style={{
                    flex: 1,
                    background: "transparent",
                    border: "none",
                    outline: "none",
                    color: "var(--text-primary)",
                    fontSize: "0.95rem",
                    resize: "none",
                    padding: "10px 12px",
                    lineHeight: 1.6,
                  }}
                />
                <button
                  type="submit"
                  disabled={!query.trim() || running}
                  style={{
                    padding: "10px 20px",
                    borderRadius: 8,
                    background: "var(--accent)",
                    color: "#fff",
                    fontWeight: 600,
                    fontSize: "0.875rem",
                    border: "none",
                    cursor: query.trim() && !running ? "pointer" : "not-allowed",
                    opacity: query.trim() && !running ? 1 : 0.5,
                    transition: "opacity 0.2s, background 0.2s",
                    whiteSpace: "nowrap",
                    alignSelf: "flex-end",
                    marginBottom: 4,
                  }}
                >
                  Generate Report →
                </button>
              </div>
            </form>

            {/* Example queries */}
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap", justifyContent: "center", marginTop: 20, maxWidth: 640 }}>
              {EXAMPLE_QUERIES.map((q) => (
                <button
                  key={q}
                  onClick={() => handleSubmit(null, q)}
                  style={{
                    background: "var(--bg-elevated)",
                    border: "1px solid var(--border)",
                    borderRadius: 20,
                    padding: "5px 14px",
                    color: "var(--text-muted)",
                    fontSize: "0.75rem",
                    cursor: "pointer",
                    transition: "color 0.2s, border-color 0.2s",
                  }}
                  onMouseEnter={(e) => {
                    (e.currentTarget as HTMLButtonElement).style.color = "var(--text-secondary)";
                    (e.currentTarget as HTMLButtonElement).style.borderColor = "var(--border-bright)";
                  }}
                  onMouseLeave={(e) => {
                    (e.currentTarget as HTMLButtonElement).style.color = "var(--text-muted)";
                    (e.currentTarget as HTMLButtonElement).style.borderColor = "var(--border)";
                  }}
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Running view */}
        {running && (
          <div
            style={{
              flex: 1,
              display: "grid",
              gridTemplateColumns: "300px 1fr",
              gap: 24,
              padding: "40px 32px",
              alignItems: "start",
            }}
          >
            <div>
              <Pipeline agents={agents} />
            </div>
            <div
              style={{
                background: "var(--bg-card)",
                border: "1px solid var(--border)",
                borderRadius: 12,
                padding: "28px 32px",
              }}
            >
              <p style={{ color: "var(--text-muted)", fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 8 }}>
                Research Question
              </p>
              <p style={{ color: "var(--text-primary)", fontSize: "1rem", lineHeight: 1.6, marginBottom: 28 }}>
                {query}
              </p>
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <div
                  style={{
                    width: 8,
                    height: 8,
                    borderRadius: "50%",
                    background: "var(--accent)",
                    animation: "pulse-ring 1.5s infinite",
                  }}
                />
                <p style={{ color: "var(--text-secondary)", fontSize: "0.875rem" }}>
                  {(() => {
                    const running = AGENT_NAMES.find((n) => agents[n]?.status === "running");
                    const done = AGENT_NAMES.filter((n) => agents[n]?.status === "done").length;
                    return running
                      ? `${running} is working…  (${done}/${AGENT_NAMES.length} agents complete)`
                      : `Starting pipeline…`;
                  })()}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div style={{ padding: "24px 32px" }}>
            <div
              style={{
                background: "rgba(239,68,68,0.1)",
                border: "1px solid rgba(239,68,68,0.3)",
                borderRadius: 10,
                padding: "16px 20px",
                color: "var(--error)",
                fontSize: "0.875rem",
              }}
            >
              <strong>Error:</strong> {error}
            </div>
          </div>
        )}

        {/* Result */}
        {result && (
          <div
            style={{
              padding: "32px",
              display: "grid",
              gridTemplateColumns: "300px 1fr",
              gap: 24,
              alignItems: "start",
            }}
          >
            {/* Left: pipeline summary + new search */}
            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
              <Pipeline agents={agents} />
              <button
                onClick={() => { setResult(null); setQuery(""); setAgents(initAgents()); }}
                style={{
                  width: "100%",
                  padding: "10px",
                  background: "var(--bg-elevated)",
                  border: "1px solid var(--border-bright)",
                  borderRadius: 8,
                  color: "var(--text-secondary)",
                  fontSize: "0.85rem",
                  fontWeight: 500,
                  cursor: "pointer",
                  transition: "background 0.2s",
                }}
              >
                + New Research
              </button>
            </div>

            {/* Right: report */}
            <ReportView result={result} query={query} />
          </div>
        )}
      </main>
    </div>
  );
}
