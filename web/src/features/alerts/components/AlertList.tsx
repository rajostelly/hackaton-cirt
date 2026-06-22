import type { AlertOut } from "@/api/types";
import { CriticityBadge, StatusBadge } from "@/shared/ui/Badge";

interface AlertListProps {
  alerts: AlertOut[];
  selectedId?: string | null;
  onSelect: (id: string) => void;
}

export function AlertList({ alerts, selectedId, onSelect }: AlertListProps) {
  if (alerts.length === 0) {
    return (
      <div className="text-center py-16 text-gray-500">
        Aucune alerte ouverte
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-gray-800">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-gray-400 border-b border-gray-800 bg-surface-alt">
            <th className="px-4 py-3 font-medium">Criticité</th>
            <th className="px-4 py-3 font-medium">Titre</th>
            <th className="px-4 py-3 font-medium">IP Source</th>
            <th className="px-4 py-3 font-medium">Règle</th>
            <th className="px-4 py-3 font-medium">Statut</th>
            <th className="px-4 py-3 font-medium">Horodatage</th>
          </tr>
        </thead>
        <tbody>
          {alerts.map((alert) => (
            <tr
              key={alert.id}
              onClick={() => onSelect(alert.id)}
              className={`border-b border-gray-800 cursor-pointer transition-colors hover:bg-surface-alt ${
                selectedId === alert.id
                  ? "bg-surface-alt ring-1 ring-inset ring-blue-600"
                  : ""
              }`}
            >
              <td className="px-4 py-3">
                <CriticityBadge criticity={alert.criticity} />
              </td>
              <td className="px-4 py-3 font-medium text-white">{alert.title}</td>
              <td className="px-4 py-3 font-mono text-gray-300">{alert.source_ip}</td>
              <td className="px-4 py-3 text-gray-300">{alert.rule_name}</td>
              <td className="px-4 py-3">
                <StatusBadge status={alert.status} />
              </td>
              <td className="px-4 py-3 text-gray-400 whitespace-nowrap">
                {new Date(alert.timestamp).toLocaleString("fr-FR")}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
