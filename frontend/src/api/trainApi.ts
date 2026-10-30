import type { TrainRun } from "../types";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "";

export async function fetchTrainRuns(): Promise<TrainRun[]> {
  const res = await fetch(`${API_BASE}/api/train/history`);
  if (!res.ok) return [];
  return res.json();
}

export async function runTrain() {
  const res = await fetch(`${API_BASE}/api/train/run`, { method: "POST" });
  return res.json();
}
