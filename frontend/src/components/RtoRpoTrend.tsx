import {
  Card,
  Text,
} from "@mantine/core";
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
  Bu veri normalde backend’den gelecek.
  Şimdilik backup alınan train’lere ait mock data.
*/
const trendData = [
  {
    time: "12:10",
    rto: 164, // saniye
    rpo: 192,
  },
  {
    time: "12:30",
    rto: 130,
    rpo: 170,
  },
];

function formatSeconds(value: number) {
  const m = Math.floor(value / 60);
  const s = value % 60;
  return `${m}m ${s}s`;
}

export default function RtoRpoTrend() {
  return (
    <Card shadow="sm" padding="lg" radius="md" withBorder mb="md">
      <Text fw={700} size="lg" mb="xs">
        RTO / RPO Trend
      </Text>

      <Text size="sm" c="dimmed" mb="md">
        Yedekleme alınan train çalışmaları için zaman içindeki RTO ve RPO değişimi
      </Text>

      <ResponsiveContainer width="100%" height={240}>
        <LineChart data={trendData}>
          <CartesianGrid strokeDasharray="3 3" />

          <XAxis dataKey="time" />

          <YAxis tickFormatter={(v) => formatSeconds(v)} />

          <Tooltip
            formatter={(value: number) => formatSeconds(value)}
            labelFormatter={(label) => `Train Time: ${label}`}
          />

          <Line
            type="monotone"
            dataKey="rto"
            stroke="#2f9e44"
            strokeWidth={2}
            dot={{ r: 4 }}
            name="RTO"
          />

          <Line
            type="monotone"
            dataKey="rpo"
            stroke="#1c7ed6"
            strokeWidth={2}
            dot={{ r: 4 }}
            name="RPO"
          />
        </LineChart>
      </ResponsiveContainer>
    </Card>
  );
}
