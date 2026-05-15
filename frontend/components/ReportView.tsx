"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { ResearchResult } from "@/lib/types";

interface Props {
  result: ResearchResult;
  query: string;
}

type Tab = "report" | "plan" | "findings" | "factcheck" | "quality";

const TABS: { id: Tab; label: string }[] = [
  { id: "report",    label: "Report" },
  { id: "plan",      label: "Research Plan" },
  { id: "findings",  label: "Findings" },
  { id: "factcheck", label: "Fact Check" },
  { id: "quality",   label: "Quality" },
];

function ScoreBadge({ score }: { score: number }) {
  const pass = score >= 70;
  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 6,
        padding: "4px 14px",
        borderRadius: 20,
        fontWeight: 700,
        fontSize: "0.9rem",
        background: pass ? "rgba(34,197,94,0.12)" : "rgba(245,158,11,0.12)",
        color: pass ? "var(--success)" : "var(--warning)",
        border: `1px solid ${pass ? "rgba(34,197,94,0.25)" : "rgba(245,158,11,0.25)"}`,
      }}
    >
      {pass ? "✓" : "⚠"} {score}/100
    </span>
  );
}

export default function ReportView({ result, query }: Props) {
  const [activeTab, setActiveTab] = useState<Tab>("report");
  const [exporting, setExporting] = useState(false);

  const content: Record<Tab, string> = {
    report:    result.final_report,
    plan:      result.research_plan,
    findings:  result.findings,
    factcheck: result.fact_check,
    quality:   result.quality_check,
  };

  async function handlePdfExport() {
    setExporting(true);
    try {
      const { jsPDF } = await import("jspdf");
      const doc = new jsPDF({ orientation: "portrait", unit: "mm", format: "a4" });
      const margin = 18;
      const pageW = doc.internal.pageSize.getWidth();
      const maxW = pageW - margin * 2;

      // Title
      doc.setFontSize(20);
      doc.setTextColor(99, 102, 241);
      doc.text("Lumern Research Report", margin, 24);

      doc.setFontSize(10);
      doc.setTextColor(148, 163, 184);
      const wrappedQ = doc.splitTextToSize(`Query: ${query}`, maxW);
      doc.text(wrappedQ, margin, 32);

      doc.setDrawColor(30, 30, 46);
      doc.line(margin, 38, pageW - margin, 38);

      // Strip markdown for PDF
      const clean = result.final_report
        .replace(/#{1,6}\s*/g, "")
        .replace(/\*\*(.*?)\*\*/g, "$1")
        .replace(/\*(.*?)\*/g, "$1")
        .replace(/`(.*?)`/g, "$1")
        .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1");

      doc.setFontSize(9.5);
      doc.setTextColor(226, 232, 240);

      let y = 44;
      const lines = clean.split("\n");
      for (const line of lines) {
        if (y > doc.internal.pageSize.getHeight() - margin) {
          doc.addPage();
          y = margin;
        }
        if (!line.trim()) { y += 3; continue; }
        const wrapped = doc.splitTextToSize(line.trim(), maxW);
        doc.text(wrapped, margin, y);
        y += wrapped.length * 5 + 1;
      }

      doc.save("lumern_report.pdf");
    } catch (e) {
      console.error(e);
    } finally {
      setExporting(false);
    }
  }

  function handleMdExport() {
    const blob = new Blob([result.final_report], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "lumern_report.md";
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div style={{ background: "var(--bg-card)", border: "1px solid var(--border)", borderRadius: 12 }}>
      {/* Header */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "16px 20px",
          borderBottom: "1px solid var(--border)",
          flexWrap: "wrap",
          gap: 12,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <ScoreBadge score={result.quality_score} />
          {result.revision_count > 1 && (
            <span style={{ color: "var(--text-muted)", fontSize: "0.75rem" }}>
              {result.revision_count - 1} revision{result.revision_count > 2 ? "s" : ""}
            </span>
          )}
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <button onClick={handleMdExport} className="btn-secondary">
            ↓ Markdown
          </button>
          <button onClick={handlePdfExport} disabled={exporting} className="btn-primary">
            {exporting ? "Exporting…" : "↓ PDF"}
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: "flex", borderBottom: "1px solid var(--border)", padding: "0 20px" }}>
        {TABS.map((tab) => {
          const active = tab.id === activeTab;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                padding: "12px 16px",
                fontSize: "0.8rem",
                fontWeight: active ? 600 : 400,
                color: active ? "var(--accent-hover)" : "var(--text-muted)",
                background: "transparent",
                border: "none",
                borderBottom: active ? "2px solid var(--accent)" : "2px solid transparent",
                cursor: "pointer",
                transition: "color 0.2s",
                whiteSpace: "nowrap",
              }}
            >
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Content */}
      <div style={{ padding: "24px 28px", maxHeight: "70vh", overflowY: "auto" }}>
        <div className="report-content">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              a: ({ href, children }) => (
                <a href={href} target="_blank" rel="noopener noreferrer">{children}</a>
              ),
            }}
          >
            {content[activeTab] ?? "_No data available_"}
          </ReactMarkdown>
        </div>
      </div>
    </div>
  );
}
