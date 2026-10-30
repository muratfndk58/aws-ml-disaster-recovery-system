import type { Metric } from "../types";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "";

export async function fetchMetrics(): Promise<Metric[]> {
  const res = await fetch(`${API_BASE}/api/metrics`);
  if (!res.ok) return [];
  return res.json();
}

