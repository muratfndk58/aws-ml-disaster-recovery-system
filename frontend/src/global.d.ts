export {};

declare global {
  interface Window {
    reloadAnomalies?: () => Promise<void>;
  }
}
