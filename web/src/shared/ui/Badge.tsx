import type { AlertStatus, Criticity } from "@/api/types";

const CRITICITY_CLASSES: Record<Criticity, string> = {
  critical: "bg-red-950/70 text-red-400 border border-red-900/50",
  high:     "bg-gray-900 text-gray-300 border border-gray-800",
  medium:   "bg-gray-900 text-gray-400 border border-gray-800",
  low:      "bg-gray-900 text-gray-500 border border-gray-800",
};

const CRITICITY_LABELS: Record<Criticity, string> = {
  critical: "Critique",
  high:     "Élevée",
  medium:   "Moyenne",
  low:      "Faible",
};

const STATUS_CLASSES: Record<AlertStatus, string> = {
  open:    "bg-gray-900 text-gray-300 border border-gray-800",
  triaged: "bg-gray-900 text-blue-400/80 border border-gray-800",
  closed:  "bg-gray-900 text-gray-600 border border-gray-800",
};

const STATUS_LABELS: Record<AlertStatus, string> = {
  open:    "Ouvert",
  triaged: "Trié",
  closed:  "Fermé",
};

export function CriticityBadge({ criticity }: { criticity: Criticity }) {
  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium tracking-wide ${CRITICITY_CLASSES[criticity]}`}
    >
      {criticity === "critical" && (
        <span className="w-1 h-1 rounded-full bg-red-500 mr-1.5 animate-pulse" />
      )}
      {CRITICITY_LABELS[criticity]}
    </span>
  );
}

export function StatusBadge({ status }: { status: AlertStatus }) {
  return (
    <span
      className={`inline-block px-2 py-0.5 rounded text-xs font-medium tracking-wide ${STATUS_CLASSES[status]}`}
    >
      {STATUS_LABELS[status]}
    </span>
  );
}
