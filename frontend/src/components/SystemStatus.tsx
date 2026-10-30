import { Card, Group, Badge, Text } from "@mantine/core";

export default function SystemStatus() {
  return (
    <Card shadow="sm" padding="lg" radius="md" withBorder>
      <Group justify="space-between">
        <Text fw={600} size="lg">
          System Status
        </Text>
        <Badge color="green" size="lg">
          STABLE
        </Badge>
      </Group>

      <Group mt="md" gap="sm">
        <Badge color="red" variant="filled">
          RISK: CRITICAL
        </Badge>
        <Badge color="blue" variant="filled">
          ACTIVE: GREEN
        </Badge>
        <Badge color="orange" variant="filled">
          RTO: 2m 34s
        </Badge>
        <Badge color="gray" variant="filled">
          RPO: 3m 12s
        </Badge>
      </Group>
    </Card>
  );
}
