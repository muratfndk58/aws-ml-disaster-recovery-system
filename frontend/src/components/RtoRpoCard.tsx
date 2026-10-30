import { Card, Text, Group, Badge, Divider } from "@mantine/core";

type RtoRpoData = {
  rtoSeconds: number;
  rpoSeconds: number;
  lastFailover?: string;
};

const mockData: RtoRpoData = {
  rtoSeconds: 164, // 2 dk 44 sn
  rpoSeconds: 192, // 3 dk 12 sn
  lastFailover: "2026-01-01 12:04",
};

function formatDuration(seconds: number) {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}m ${s}s`;
}

function rtoColor(seconds: number) {
  if (seconds <= 180) return "green"; // < 3 dk
  if (seconds <= 300) return "yellow";
  return "red";
}

function rpoColor(seconds: number) {
  if (seconds <= 300) return "green"; // < 5 dk
  if (seconds <= 600) return "yellow";
  return "red";
}

export default function RtoRpoCard() {
  return (
    <Card shadow="sm" padding="lg" radius="md" withBorder>
      <Text fw={700} size="lg">
        RTO / RPO Overview
      </Text>

      <Text size="sm" c="dimmed" mb="md">
        Son gerçekleşen failover’a göre hesaplanan değerler
      </Text>

      <Group justify="space-between" mb="sm">
        <Text fw={600}>RTO (Recovery Time)</Text>
        <Badge color={rtoColor(mockData.rtoSeconds)}>
          {formatDuration(mockData.rtoSeconds)}
        </Badge>
      </Group>

      <Group justify="space-between">
        <Text fw={600}>RPO (Data Loss Window)</Text>
        <Badge color={rpoColor(mockData.rpoSeconds)}>
          {formatDuration(mockData.rpoSeconds)}
        </Badge>
      </Group>

      <Divider my="md" />

      <Text size="sm" c="dimmed">
        Last failover: {mockData.lastFailover ?? "N/A"}
      </Text>
    </Card>
  );
}
