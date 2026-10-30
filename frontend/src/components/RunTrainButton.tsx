import { Button } from "@mantine/core";
import { runTrain } from "../api/trainApi";

type Props = {
  onCompleted: () => void;
};

export default function RunTrainButton({ onCompleted }: Props) {
  const handleClick = async () => {
    try {
      await runTrain();
      onCompleted();
    } catch (err) {
      console.error("Train error:", err);
      alert("Train failed – console'a bak");
    }
  };

  return (
    <Button color="blue" mb="md" onClick={handleClick}>
      ▶️ Run Train
    </Button>
  );
}
