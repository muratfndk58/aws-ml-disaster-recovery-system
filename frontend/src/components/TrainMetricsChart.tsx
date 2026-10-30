import { Card, Text, Group, Badge } from "@mantine/core";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

/*
  Her nokta = 1 train (30 dk)
  Değerler: son 30 dk ortalaması / max simülasyonu
*/
const trainMetrics = [
  {
    trainTime: "12:00",
    cpu: 68,
    ram: 55,
    disk: 42,
  },
  {
    trainTime: "12:30",
    cpu: 82,
    ram: 61,
    disk: 70,
  },
  {
    trainTime: "13:00",
    cpu: 60,
    ram: 50,
    disk: 45,
  },
];

function getRisk(cpu: number, ram: number, disk: number) {
  if (cpu > 80 || disk > 75) return "CRITICAL";
  if (cpu > 70 || ram > 70) return "HIGH";
  if (cpu > 60) return "MEDIUM";
  return "LOW";
}

function riskColor(risk: string) {
  if (risk === "CRITICAL") return "red";
  if (risk === "HIGH") return "orange";
  if (risk === "MEDIUM") return "yellow";
  return "green";
}

export default function TrainMetricsChart() {
  const latest = trainMetrics[trainMetrics.length - 1];
  const risk = getRisk(latest.cpu, latest.ram, latest.disk);

  return (
    <Card shadow="sm" padding="lg" radius="md" withBorder mb="md">
      <Group justify="space-between" mb="sm">
        <Text fw={700} size="lg">
          System Metrics (Train-based, 30 min)
        </Text>
        <Badge color={riskColor(risk)}>{risk}</Badge>
      </Group>

      <Text size="sm" c="dimmed" mb="md">
        Each point represents aggregated metrics from the last 30 minutes
      </Text>

      <ResponsiveContainer width="100%" height={260}>
        <LineChart data={trainMetrics}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="trainTime" />
          <YAxis domain={[0, 100]} tickFormatter={(v) => `${v}%`} />
          <Tooltip formatter={(v: number) => `${v}%`} />

          <Line
            type="monotone"
            dataKey="cpu"
            stroke="#fa5252"
            strokeWidth={2}
            dot={{ r: 4 }}
            name="CPU avg %"
          />

          <Line
            type="monotone"
            dataKey="ram"
            stroke="#339af0"
            strokeWidth={2}
            dot={{ r: 4 }}
            name="RAM avg %"
          />

          <Line
            type="monotone"
            dataKey="disk"
            stroke="#f59f00"
            strokeWidth={2}
            dot={{ r: 4 }}
            name="Disk avg %"
          />
        </LineChart>
      </ResponsiveContainer>
    </Card>
  );
}
