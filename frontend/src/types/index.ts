export type BackupItem = {
  path: string;
  size_mb: number;
};

export type TrainRun = {
  date: string;
  time: string;
  backup: "TAKEN" | "SKIPPED";
  rto_seconds: number | null;
  rpo_seconds: number | null;
  backup_items: BackupItem[];
  total_backup_mb: number | null;
};

export type Metric = {
  timestamp: string;
  cpu_percent: number;
  ram_percent: number;
  disk_percent: number;
};

export type Anomaly = {
  timestamp: string;
  cpu: boolean;
  ram: boolean;
};
