import type { AlertStatus, Criticity } from "@/api/types";

const CRITICITY_CLASSES: Record<Criticity, string> = {
  critical: "bg-criticity-critical text-white",
  high: "bg-criticity-high text-white",
  medium: "bg-criticity-medium text-white",
  low: "bg-criticity-low text-white",
};

const STATUS_CLASSES: Record<AlertStatus, string> = {
  open: "bg-red-900 text-red-200",
  triaged: "bg-purple-900 text-purple-200",
  closed: "bg-gray-700 text-gray-300",
};

export function CriticityBadge({ criticity }: { criticity: Criticity }) {
  return (
    <span
      className={`inline-block px-2 py-0.5 rounded text-xs font-semibold uppercase tracking-wide ${CRITICITY_CLASSES[criticity]}`}
    >
      {criticity}
    </span>
  );
}

export function StatusBadge({ status }: { status: AlertStatus }) {
  return (
    <span
      className={`inline-block px-2 py-0.5 rounded text-xs font-semibold uppercase tracking-wide ${STATUS_CLASSES[status]}`}
    >
      {status}
    </span>
  );
}
