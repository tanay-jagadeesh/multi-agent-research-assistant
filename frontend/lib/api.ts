import type { AgentState, ResearchResult, HistoryItem } from "./types";

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function startResearch(query: string): Promise<string> {
  const res = await fetch(`${BASE}/api/research`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });
  if (!res.ok) throw new Error("Failed to start research");
  const data = await res.json();
  return data.job_id as string;
}

export function streamResearch(
  jobId: string,
  onProgress: (agent: string, status: string, elapsed: number) => void,
  onResult: (result: ResearchResult) => void,
  onError: (msg: string) => void
): () => void {
  const es = new EventSource(`${BASE}/api/research/${jobId}/stream`);

  es.onmessage = (e) => {
    try {
      const msg = JSON.parse(e.data);
      if (msg.type === "progress") {
        onProgress(msg.agent, msg.status, msg.elapsed ?? 0);
      } else if (msg.type === "result") {
        onResult(msg as ResearchResult);
        es.close();
      } else if (msg.type === "error") {
        onError(msg.message);
        es.close();
      }
    } catch {
      // ignore parse errors
    }
  };

  es.onerror = () => {
    onError("Connection lost. Please try again.");
    es.close();
  };

  return () => es.close();
}

export async function fetchHistory(): Promise<HistoryItem[]> {
  try {
    const res = await fetch(`${BASE}/api/history`);
    if (!res.ok) return [];
    const data = await res.json();
    return (data.history ?? []) as HistoryItem[];
  } catch {
    return [];
  }
}
