import type { ReactNode } from "react";
import type { AlertOut } from "@/api/types";
import { CriticityBadge, StatusBadge } from "@/shared/ui/Badge";
import { useTriageAlert } from "../hooks/useAlerts";

interface AlertDetailProps {
  alert: AlertOut;
  onClose: () => void;
}

export function AlertDetail({ alert, onClose }: AlertDetailProps) {
  const triage = useTriageAlert();

  return (
    <div className="bg-surface-alt border border-gray-700 rounded-lg p-6 flex flex-col gap-5">
      <div className="flex justify-between items-start">
        <h2 className="text-lg font-bold leading-snug pr-4">{alert.title}</h2>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-white text-xl leading-none shrink-0"
          aria-label="Fermer"
        >
          ×
        </button>
      </div>

      <div className="grid grid-cols-2 gap-4 text-sm">
        <Field label="Criticité">
          <CriticityBadge criticity={alert.criticity} />
        </Field>
        <Field label="Statut">
          <StatusBadge status={alert.status} />
        </Field>
        <Field label="IP Source">
          <span className="font-mono">{alert.source_ip}</span>
        </Field>
        {alert.destination_ip && (
          <Field label="IP Destination">
            <span className="font-mono">{alert.destination_ip}</span>
          </Field>
        )}
        <Field label="Règle">{alert.rule_name}</Field>
        <Field label="Horodatage">
          {new Date(alert.timestamp).toLocaleString("fr-FR")}
        </Field>
      </div>

      {alert.explanation && (
        <div className="bg-gray-900 border border-gray-700 rounded p-4">
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">
            Analyse IA
          </p>
          <p className="text-sm leading-relaxed text-gray-200">{alert.explanation}</p>
        </div>
      )}

      {alert.status === "open" && (
        <div className="flex gap-3">
          <button
            onClick={() => triage.mutate({ id: alert.id, isFalsePositive: false })}
            disabled={triage.isPending}
            className="flex-1 py-2 rounded font-medium text-sm bg-red-800 hover:bg-red-700 disabled:opacity-50 transition-colors"
          >
            Vrai positif
          </button>
          <button
            onClick={() => triage.mutate({ id: alert.id, isFalsePositive: true })}
            disabled={triage.isPending}
            className="flex-1 py-2 rounded font-medium text-sm bg-gray-700 hover:bg-gray-600 disabled:opacity-50 transition-colors"
          >
            Faux positif
          </button>
        </div>
      )}

      {alert.is_false_positive != null && (
        <p className="text-sm text-gray-400">
          Verdict :{" "}
          <span className={alert.is_false_positive ? "text-gray-300" : "text-red-400"}>
            {alert.is_false_positive ? "Faux positif" : "Vrai positif"}
          </span>
        </p>
      )}
    </div>
  );
}

function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div>
      <p className="text-xs text-gray-400 mb-1">{label}</p>
      <div className="text-sm text-white">{children}</div>
    </div>
  );
}
