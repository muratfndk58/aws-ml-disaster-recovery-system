import type { Anomaly } from "../types";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "";

export async function fetchAnomalies(): Promise<Anomaly[]> {
  const res = await fetch(`${API_BASE}/api/anomalies`);
  if (!res.ok) return [];
  return res.json();
}
