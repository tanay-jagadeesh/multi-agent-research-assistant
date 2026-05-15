export type AgentStatus = "waiting" | "running" | "done" | "error";

export interface AgentState {
  name: string;
  status: AgentStatus;
  elapsed?: number;
}

export interface ResearchResult {
  final_report: string;
  research_plan: string;
  findings: string;
  fact_check: string;
  citations: string;
  quality_check: string;
  quality_score: number;
  revision_count: number;
}

export interface HistoryItem {
  id: string;
  query: string;
  quality_score: number;
  created_at: string;
}
