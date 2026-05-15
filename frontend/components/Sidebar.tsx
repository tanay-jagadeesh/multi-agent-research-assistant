"use client";

import { useEffect, useState } from "react";
import { fetchHistory } from "@/lib/api";
import type { HistoryItem } from "@/lib/types";

interface Props {
  onLoadReport?: (query: string) => void;
}

export default function Sidebar({ onLoadReport }: Props) {
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHistory().then((h) => { setHistory(h); setLoading(false); });
  }, []);

  return (
    <aside
      style={{
        width: 260,
        minWidth: 220,
        background: "var(--bg-card)",
        borderRight: "1px solid var(--border)",
        display: "flex",
        flexDirection: "column",
        height: "100vh",
        position: "sticky",
        top: 0,
        overflowY: "auto",
      }}
    >
      {/* Brand */}
      <div style={{ padding: "20px 18px 12px", borderBottom: "1px solid var(--border)" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{ fontSize: "1.25rem" }}>🔬</span>
          <span style={{ fontWeight: 700, fontSize: "1rem", color: "var(--text-primary)" }}>Lumern</span>
        </div>
        <p style={{ color: "var(--text-muted)", fontSize: "0.7rem", marginTop: 4 }}>
          AI Research Assistant
        </p>
      </div>

      {/* History */}
      <div style={{ padding: "14px 14px 0" }}>
        <p style={{ color: "var(--text-muted)", fontSize: "0.7rem", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 10 }}>
          Recent Reports
        </p>

        {loading && (
          <>
            {[1, 2, 3].map((n) => (
              <div key={n} className="shimmer" style={{ height: 48, borderRadius: 6, marginBottom: 6 }} />
            ))}
          </>
        )}

        {!loading && history.length === 0 && (
          <p style={{ color: "var(--text-muted)", fontSize: "0.78rem", lineHeight: 1.5 }}>
            No reports yet. Generate your first research report to see history here.
          </p>
        )}

        {history.map((item) => (
          <button
            key={item.id}
            onClick={() => onLoadReport?.(item.query)}
            style={{
              display: "block",
              width: "100%",
              textAlign: "left",
              padding: "10px 10px",
              borderRadius: 7,
              border: "1px solid transparent",
              background: "transparent",
              cursor: "pointer",
              marginBottom: 4,
              transition: "background 0.2s, border-color 0.2s",
            }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLButtonElement).style.background = "var(--bg-elevated)";
              (e.currentTarget as HTMLButtonElement).style.borderColor = "var(--border-bright)";
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLButtonElement).style.background = "transparent";
              (e.currentTarget as HTMLButtonElement).style.borderColor = "transparent";
            }}
          >
            <p style={{ color: "var(--text-secondary)", fontSize: "0.78rem", lineHeight: 1.4, marginBottom: 4 }}>
              {item.query.length > 55 ? item.query.slice(0, 55) + "…" : item.query}
            </p>
            <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
              <span
                style={{
                  fontSize: "0.65rem",
                  fontWeight: 700,
                  padding: "2px 6px",
                  borderRadius: 10,
                  background: item.quality_score >= 70 ? "rgba(34,197,94,0.12)" : "rgba(245,158,11,0.12)",
                  color: item.quality_score >= 70 ? "var(--success)" : "var(--warning)",
                }}
              >
                {item.quality_score}/100
              </span>
              <span style={{ color: "var(--text-muted)", fontSize: "0.65rem" }}>
                {item.created_at?.slice(0, 10)}
              </span>
            </div>
          </button>
        ))}
      </div>

      {/* Footer */}
      <div style={{ marginTop: "auto", padding: "14px 18px", borderTop: "1px solid var(--border)" }}>
        <p style={{ color: "var(--text-muted)", fontSize: "0.65rem", lineHeight: 1.6 }}>
          6-agent pipeline · Planner → Researcher → Fact Checker → Citation → Analyst → QC
        </p>
      </div>
    </aside>
  );
}
