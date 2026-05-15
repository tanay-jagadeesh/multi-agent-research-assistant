"use client";

import type { AgentState, AgentStatus } from "@/lib/types";

const AGENTS: { name: string; label: string; subtitle: string }[] = [
  { name: "Planner",         label: "Planner",         subtitle: "Decomposes your question" },
  { name: "Researcher",      label: "Researcher",       subtitle: "Gathers web sources" },
  { name: "Fact-Checker",    label: "Fact Checker",     subtitle: "Verifies every claim" },
  { name: "Citation",        label: "Citation",         subtitle: "Formats bibliography" },
  { name: "Analyst",         label: "Analyst",          subtitle: "Synthesizes the report" },
  { name: "Quality Control", label: "Quality Control",  subtitle: "Scores & revises" },
];

const ICON: Record<AgentStatus, string> = {
  waiting: "○",
  running: "◉",
  done:    "✓",
  error:   "✕",
};

const COLOR: Record<AgentStatus, string> = {
  waiting: "var(--text-muted)",
  running: "var(--accent)",
  done:    "var(--success)",
  error:   "var(--error)",
};

interface Props {
  agents: Record<string, AgentState>;
}

export default function Pipeline({ agents }: Props) {
  return (
    <div
      style={{
        background: "var(--bg-card)",
        border: "1px solid var(--border)",
        borderRadius: 12,
        padding: "20px 24px",
      }}
    >
      <p style={{ color: "var(--text-muted)", fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 16 }}>
        Pipeline
      </p>
      {AGENTS.map((a, i) => {
        const state = agents[a.name] ?? { name: a.name, status: "waiting" };
        const isRunning = state.status === "running";
        const color = COLOR[state.status];

        return (
          <div key={a.name}>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 12,
                padding: "10px 12px",
                borderRadius: 8,
                background: isRunning ? "var(--accent-dim)" : "transparent",
                transition: "background 0.3s",
              }}
            >
              {/* Icon */}
              <span
                className={isRunning ? "agent-running" : undefined}
                style={{
                  color,
                  fontSize: "1rem",
                  width: 20,
                  textAlign: "center",
                  fontWeight: 700,
                  display: "inline-block",
                  borderRadius: "50%",
                  transition: "color 0.3s",
                }}
              >
                {ICON[state.status]}
              </span>

              {/* Label */}
              <div style={{ flex: 1, minWidth: 0 }}>
                <p style={{ color, fontWeight: 600, fontSize: "0.875rem", transition: "color 0.3s" }}>
                  {a.label}
                </p>
                <p style={{ color: "var(--text-muted)", fontSize: "0.75rem", marginTop: 1 }}>
                  {isRunning ? a.subtitle + "…" : a.subtitle}
                </p>
              </div>

              {/* Elapsed */}
              {state.elapsed != null && state.status === "done" && (
                <span style={{ color: "var(--text-muted)", fontSize: "0.7rem", fontFamily: "monospace" }}>
                  {state.elapsed.toFixed(1)}s
                </span>
              )}
            </div>

            {/* Arrow connector */}
            {i < AGENTS.length - 1 && (
              <div
                style={{
                  textAlign: "center",
                  color: state.status === "done" ? "var(--success)" : "var(--border-bright)",
                  fontSize: "0.75rem",
                  lineHeight: "16px",
                  transition: "color 0.4s",
                }}
              >
                ↓
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

export { AGENTS };
