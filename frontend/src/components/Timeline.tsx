import { Card, Text, List, Badge, Group } from "@mantine/core";

const events = [
  {
    time: "12:02:10",
    type: "info",
    message: "CPU spike detected (85%)",
  },
  {
    time: "12:02:18",
    type: "critical",
    message: "ML anomaly detected → CRITICAL",
  },
  {
    time: "12:02:19",
    type: "incident",
    message: "Incident started (inc-20260101-004)",
  },
  {
    time: "12:02:30",
    type: "snapshot",
    message: "Snapshot created from BLUE instance",
  },
  {
    time: "12:04:10",
    type: "ami",
    message: "AMI registered and available",
  },
  {
    time: "12:04:30",
    type: "green",
    message: "GREEN instance is READY",
  },
  {
    time: "12:04:44",
    type: "failover",
    message: "Elastic IP moved to GREEN (Failover)",
  },
];

function getBadge(type: string) {
  switch (type) {
    case "critical":
      return <Badge color="red">CRITICAL</Badge>;
    case "snapshot":
      return <Badge color="blue">SNAPSHOT</Badge>;
    case "ami":
      return <Badge color="violet">AMI</Badge>;
    case "green":
      return <Badge color="green">GREEN</Badge>;
    case "failover":
      return <Badge color="orange">FAILOVER</Badge>;
    case "incident":
      return <Badge color="gray">INCIDENT</Badge>;
    default:
      return <Badge color="dark">INFO</Badge>;
  }
}

export default function Timeline() {
  return (
    <Card shadow="sm" padding="lg" radius="md" withBorder mt="lg">
      <Text fw={600} size="lg" mb="md">
        Incident Timeline
      </Text>

      <List spacing="sm" size="sm">
        {events.map((event, index) => (
          <List.Item key={index}>
            <Group gap="sm">
              <Text fw={500} w={80}>
                {event.time}
              </Text>
              {getBadge(event.type)}
              <Text>{event.message}</Text>
            </Group>
          </List.Item>
        ))}
      </List>
    </Card>
  );
}
