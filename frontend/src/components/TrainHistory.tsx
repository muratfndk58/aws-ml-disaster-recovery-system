import { useState } from "react";
import {
  Table,
  Badge,
  Text,
  Group,
  Modal,
  Code,
} from "@mantine/core";
import type { TrainRun } from "../types";

type Props = {
  runs: TrainRun[];
};

export default function TrainHistory({ runs }: Props) {
  const [selectedRun, setSelectedRun] = useState<TrainRun | null>(null);

  return (
    <>
      <Table striped highlightOnHover>

        <thead>
          <tr>
            <th>Time</th>
            <th>Backup</th>
            <th>RTO</th>
            <th>RPO</th>
            <th>Backup Summary</th>
          </tr>
        </thead>

        <tbody>
          {runs.map((run, i) => (
            <tr
              key={i}
              onClick={() => setSelectedRun(run)}
              style={{ cursor: "pointer" }}
            >
              <td>{run.time}</td>

              {/* BACKUP STATUS */}
              <td>
                {run.backup === "TAKEN" ? (
                  <Badge color="green">TAKEN</Badge>
                ) : (
                  <Badge color="gray">SKIPPED</Badge>
                )}
              </td>

              {/* RTO */}
              <td>
                {run.rto_seconds ? (
                  <Badge color="green">
                    {Math.floor(run.rto_seconds / 60)}m{" "}
                    {Math.floor(run.rto_seconds % 60)}s
                  </Badge>
                ) : (
                  "—"
                )}
              </td>

              {/* RPO */}
              <td>
                {run.rpo_seconds ? (
                  <Badge color="blue">
                    {Math.floor(run.rpo_seconds / 60)}m{" "}
                    {Math.floor(run.rpo_seconds % 60)}s
                  </Badge>
                ) : (
                  "—"
                )}
              </td>

              {/* BACKUP SUMMARY */}
              <td>
                {run.backup === "TAKEN" ? (
                  <Group gap={6}>
                    <Text size="sm">
                      {run.backup_items?.length ?? 0} item(s)
                    </Text>
                    <Badge color="indigo">
                      {run.total_backup_mb} MB
                    </Badge>
                  </Group>
                ) : (
                  <Text c="dimmed">—</Text>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </Table>

      {/* 🔍 BACKUP DETAILS MODAL */}
      <Modal
        opened={!!selectedRun}
        onClose={() => setSelectedRun(null)}
        title="Backup Details"
        size="lg"
      >
        {selectedRun?.backup === "TAKEN" ? (
          <Table>
            <thead>
              <tr>
                <th>Path</th>
                <th>Size (MB)</th>
              </tr>
            </thead>
            <tbody>
              {selectedRun.backup_items.map((item, idx) => (
                <tr key={idx}>
                  <td>
                    <Code>{item.path}</Code>
                  </td>
                  <td>{item.size_mb} MB</td>
                </tr>
              ))}
            </tbody>
          </Table>
        ) : (
          <Text c="dimmed">
            Bu run için yedekleme yapılmadı.
          </Text>
        )}
      </Modal>
    </>
  );
}
