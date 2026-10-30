import { useEffect, useState } from "react";
import { Card, Title } from "@mantine/core";
import {
  Chart as ChartJS,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Tooltip,
  Legend,
} from "chart.js";
import { Line } from "react-chartjs-2";

import { fetchMetrics } from "../api/metricsApi";

ChartJS.register(
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Tooltip,
  Legend
);

type Metric = {
  timestamp: string;
  cpu_percent: number;
  ram_percent: number;
  disk_percent: number;
};

export default function LiveMetricsChart() {
  const [metrics, setMetrics] = useState<Metric[]>([]);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await fetchMetrics();
        setMetrics(data.slice(-20)); // son 20 nokta
      } catch (e) {
        console.error(e);
      }
    };

    load();
    const i = setInterval(load, 2000); // 2 sn
    return () => clearInterval(i);
  }, []);

  const labels = metrics.map((m) =>
    new Date(m.timestamp).toLocaleTimeString()
  );

  const data = {
    labels,
    datasets: [
      {
        label: "CPU %",
        data: metrics.map((m) => m.cpu_percent),
        borderColor: "rgba(255, 99, 132, 1)",
        backgroundColor: "rgba(255, 99, 132, 0.15)",
        tension: 0.45,            // 🔥 DALGALANMA
        borderWidth: 3,
        pointRadius: 0,
      },
      {
        label: "RAM %",
        data: metrics.map((m) => m.ram_percent),
        borderColor: "rgba(54, 162, 235, 1)",
        backgroundColor: "rgba(54, 162, 235, 0.15)",
        tension: 0.45,
        borderWidth: 3,
        pointRadius: 0,
      },
      {
        label: "Disk %",
        data: metrics.map((m) => m.disk_percent),
        borderColor: "rgba(75, 192, 192, 1)",
        backgroundColor: "rgba(75, 192, 192, 0.15)",
        tension: 0.45,
        borderWidth: 3,
        pointRadius: 0,
      },
    ],
  };

  const options = {
  responsive: true,
  animation: {
    duration: 700,
    easing: "easeInOutQuart" as const, // ✅ FIX
  },
  plugins: {
    legend: {
      position: "top" as const,
    },
  },
  scales: {
    y: {
      min: 0,
      max: 100,
      grid: {
        color: "rgba(0,0,0,0.05)",
      },
    },
    x: {
      grid: {
        display: false,
      },
    },
  },
};


  return (
    <Card withBorder shadow="sm">
      <Title order={4} mb="sm">
        Live System Metrics
      </Title>
      <Line data={data} options={options} />
    </Card>
  );
}
