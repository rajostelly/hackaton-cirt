import { useState } from "react";
import type { AlertOut, Criticity } from "@/api/types";
import { CriticityBadge } from "@/shared/ui/Badge";
import { LoadingSpinner } from "@/shared/ui/LoadingSpinner";
import { AlertDetail } from "@/features/alerts/components/AlertDetail";
import { AlertList } from "@/features/alerts/components/AlertList";
import { LiveScanToast } from "@/features/alerts/components/LiveScanToast";
import { useOpenAlerts } from "@/features/alerts/hooks/useAlerts";
import { useAlertStream } from "@/features/alerts/hooks/useAlertStream";

const CRITICITIES: Criticity[] = ["critical", "high", "medium", "low"];

const CRITICITY_LABELS: Record<Criticity, string> = {
  critical: "Critique",
  high: "Élevée",
  medium: "Moyenne",
  low: "Faible",
};

export function Dashboard() {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [liveScans, setLiveScans] = useState<AlertOut[]>([]);
  const { data: alerts = [], isLoading, error } = useOpenAlerts();

  const { status: streamStatus } = useAlertStream((event) => {
    if (event.type === "alert.created") {
      setLiveScans((prev) => [event.data, ...prev].slice(0, 4));
    }
  });

  const selectedAlert: AlertOut | undefined = alerts.find((a) => a.id === selectedId);

  function handleSelect(id: string) {
    setSelectedId((prev) => (prev === id ? null : id));
  }

  function dismissScan(id: string) {
    setLiveScans((prev) => prev.filter((s) => s.id !== id));
  }

  const isLive = streamStatus === "open";

  return (
    <div className="min-h-screen bg-surface text-white flex flex-col">
      <header className="border-b border-gray-800 px-6 py-4 flex items-center gap-3">
        <span className="text-lg font-bold tracking-tight">ARO</span>
        <span className="text-gray-500 text-sm">· Security Operations Center</span>
        <div className="ml-auto flex items-center gap-2 text-xs text-gray-400">
          <span
            className={`w-2 h-2 rounded-full inline-block ${
              isLive ? "bg-green-500 animate-pulse" : "bg-gray-600"
            }`}
          />
          {isLive ? "Temps réel actif" : "Connexion…"}
        </div>
      </header>

      <main className="flex-1 p-6 flex flex-col gap-6">
        {/* Stat cards */}
        <div className="grid grid-cols-4 gap-4">
          {CRITICITIES.map((c) => (
            <div key={c} className="bg-surface-alt border border-gray-800 rounded-lg p-4">
              <div className="mb-3">
                <CriticityBadge criticity={c} />
              </div>
              <p className="text-3xl font-bold">
                {isLoading ? "—" : alerts.filter((a) => a.criticity === c).length}
              </p>
              <p className="text-gray-400 text-sm mt-1">{CRITICITY_LABELS[c]}</p>
            </div>
          ))}
        </div>

        {/* Alerts section */}
        <div
          className={selectedAlert ? "grid gap-6 items-start" : ""}
          style={selectedAlert ? { gridTemplateColumns: "1fr 380px" } : undefined}
        >
          <div className="flex flex-col gap-3">
            <h2 className="font-semibold text-white">
              Alertes ouvertes{" "}
              {!isLoading && (
                <span className="text-gray-400 font-normal text-sm">({alerts.length})</span>
              )}
            </h2>

            {isLoading && <LoadingSpinner />}

            {error && (
              <p className="text-red-400 text-sm py-4">
                Erreur de connexion à l'API — vérifiez que le backend est démarré sur le port 8000.
              </p>
            )}

            {!isLoading && !error && (
              <AlertList alerts={alerts} selectedId={selectedId} onSelect={handleSelect} />
            )}
          </div>

          {selectedAlert && (
            <AlertDetail alert={selectedAlert} onClose={() => setSelectedId(null)} />
          )}
        </div>
      </main>

      {/* Toasts temps réel : scans détectés par le capteur */}
      <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-3">
        {liveScans.map((scan) => (
          <LiveScanToast key={scan.id} alert={scan} onDismiss={() => dismissScan(scan.id)} />
        ))}
      </div>
    </div>
  );
}
