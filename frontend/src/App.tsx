import { Container, Title, Divider } from "@mantine/core";
import LiveMetricsChart from "./components/LiveMetricsChart";
import TrainHistory from "./components/TrainHistory";

import { useEffect, useState } from "react";
import { fetchTrainRuns } from "./api/trainApi";
import type { TrainRun } from "./types";

export default function App() {
  const [runs, setRuns] = useState<TrainRun[]>([]);

  useEffect(() => {
    const load = async () => {
      const data = await fetchTrainRuns();
      setRuns(data);
    };

    load();
    const interval = setInterval(load, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <Container size="lg">
      <Title order={2} mt="md">
        AWS ML-DR Dashboard
      </Title>

      <Divider my="md" />

      {/* 🔴 SADECE GRAFİK */}
      <LiveMetricsChart />

      {/* 🔴 ALT BİLGİ KUTULARI KALIYOR */}
      <TrainHistory runs={runs} />
    </Container>
  );
}
