import { Radar, RefreshCw, Wifi, WifiOff } from "lucide-react";
import type { AlertOut } from "@/api/types";
import { CriticityBadge } from "@/shared/ui/Badge";
import { useOpenAlerts } from "@/features/alerts/hooks/useAlerts";
import { useAlertStream } from "@/features/alerts/hooks/useAlertStream";

export function ScansPage() {
  const { data: alerts = [], isLoading, refetch } = useOpenAlerts();
  const { status: streamStatus } = useAlertStream();

  const isLive = streamStatus === "open";

  const scanAlerts = alerts.filter(
    (a) =>
      a.rule_name.toLowerCase().includes("scan") ||
      a.rule_name.toLowerCase().includes("nmap") ||
      a.title.toLowerCase().includes("scan") ||
      a.title.toLowerCase().includes("nmap") ||
      a.title.toLowerCase().includes("port"),
  );
  const detections = scanAlerts.length > 0 ? scanAlerts : alerts;

  const sorted = [...detections].sort(
    (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime(),
  );

  const uniqueIPs = [...new Set(detections.map((a) => a.source_ip))];

  const critOrder: AlertOut["criticity"][] = ["critical", "high", "medium", "low"];

  return (
    <div className="flex flex-col min-h-full">
      {/* Header */}
      <header className="border-b border-gray-800/80 px-6 py-4 shrink-0 flex items-center justify-between">
        <div>
          <h1 className="text-base font-semibold text-white flex items-center gap-2">
            <Radar className="w-4 h-4 text-gray-500" />
            Détections réseau
          </h1>
          <p className="text-xs text-gray-600 mt-0.5">
            Scans nmap et tentatives de reconnaissance
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded text-xs ${
              isLive ? "text-green-400 bg-green-950/30" : "text-gray-600 bg-gray-900/50"
            }`}
          >
            {isLive ? <Wifi className="w-3 h-3" /> : <WifiOff className="w-3 h-3" />}
            {isLive ? "Capteur actif" : "Hors ligne"}
          </div>
          <button
            onClick={() => void refetch()}
            className="p-2 text-gray-600 hover:text-gray-300 rounded transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>
      </header>

      <main className="flex-1 p-6 flex flex-col gap-5">
        {/* Stats — same style as Dashboard cards */}
        <div className="grid grid-cols-3 gap-3">
          <StatTile label="Total détections"  value={isLoading ? "—" : String(detections.length)} />
          <StatTile label="Sources uniques"   value={isLoading ? "—" : String(uniqueIPs.length)} />
          <StatTile
            label="Critiques"
            value={isLoading ? "—" : String(detections.filter((a) => a.criticity === "critical").length)}
            warn={detections.filter((a) => a.criticity === "critical").length > 0}
          />
        </div>

        {/* Grid */}
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-5 flex-1">
          {/* Feed */}
          <div className="xl:col-span-2 bg-surface-alt border border-gray-800/80 rounded-lg overflow-hidden flex flex-col">
            <div className="px-5 py-3 border-b border-gray-800/60 flex items-center justify-between">
              <p className="text-sm font-medium text-gray-300">Flux de détection</p>
              <span className="text-xs text-gray-700 tabular-nums">
                {sorted.length} événement{sorted.length !== 1 ? "s" : ""}
              </span>
            </div>

            <div className="overflow-y-auto flex-1">
              {isLoading ? (
                <div className="flex justify-center p-8">
                  <div className="w-5 h-5 border-2 border-gray-800 border-t-blue-500 rounded-full animate-spin" />
                </div>
              ) : sorted.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-16 gap-3 text-center px-6">
                  <Radar className="w-8 h-8 text-gray-800" />
                  <p className="text-sm text-gray-600">Aucune détection enregistrée</p>
                  <p className="text-xs text-gray-700">
                    Lancez{" "}
                    <code className="font-mono bg-surface-elevated px-1 rounded">
                      simulate_scan.py
                    </code>{" "}
                    pour tester le capteur.
                  </p>
                </div>
              ) : (
                <div className="divide-y divide-gray-800/40">
                  {sorted.map((alert) => (
                    <ScanEvent key={alert.id} alert={alert} />
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* IP list */}
          <div className="bg-surface-alt border border-gray-800/80 rounded-lg overflow-hidden">
            <div className="px-5 py-3 border-b border-gray-800/60">
              <p className="text-sm font-medium text-gray-300">Sources suspectes</p>
            </div>
            <div className="p-4 flex flex-col gap-0.5">
              {uniqueIPs.length === 0 ? (
                <p className="text-sm text-gray-700 py-4">Aucune IP enregistrée</p>
              ) : (
                uniqueIPs.slice(0, 15).map((ip) => {
                  const ipAlerts = detections.filter((a) => a.source_ip === ip);
                  const count = ipAlerts.length;
                  const topCrit = ipAlerts.sort(
                    (a, b) =>
                      critOrder.indexOf(a.criticity) - critOrder.indexOf(b.criticity),
                  )[0]?.criticity ?? "low";

                  return (
                    <div
                      key={ip}
                      className="flex items-center gap-2.5 py-1.5 px-2 rounded hover:bg-surface-elevated transition-colors"
                    >
                      <CriticityBadge criticity={topCrit} />
                      <span className="font-mono text-sm text-gray-400 flex-1 truncate">
                        {ip}
                      </span>
                      <span className="text-xs text-gray-700 tabular-nums">
                        {count}×
                      </span>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

/* ── Stat tile ── */
function StatTile({
  label,
  value,
  warn,
}: {
  label: string;
  value: string;
  warn?: boolean;
}) {
  return (
    <div className="bg-surface-alt border border-gray-800/80 rounded-lg p-5">
      <p className="text-3xl font-bold text-white tabular-nums flex items-center gap-2">
        {value}
        {warn && value !== "0" && (
          <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
        )}
      </p>
      <p className="text-sm text-gray-400 mt-1.5 font-medium">{label}</p>
    </div>
  );
}

/* ── Scan event row ── */
function ScanEvent({ alert }: { alert: AlertOut }) {
  const dotColor = {
    critical: "bg-red-500",
    high:     "bg-gray-400",
    medium:   "bg-gray-600",
    low:      "bg-gray-700",
  }[alert.criticity];

  return (
    <div className="px-5 py-3 flex items-center gap-3 hover:bg-surface-elevated transition-colors">
      <div className={`w-1.5 h-1.5 rounded-full shrink-0 ${dotColor}`} />
      <div className="flex-1 min-w-0">
        <p className="text-sm text-gray-200 truncate">{alert.title}</p>
        <p className="text-xs text-gray-600 mt-0.5 truncate">
          <span className="font-mono">{alert.source_ip}</span>
          <span className="mx-1.5 text-gray-800">·</span>
          {alert.rule_name}
        </p>
      </div>
      <div className="flex items-center gap-2 shrink-0">
        <CriticityBadge criticity={alert.criticity} />
        <span className="text-xs text-gray-700 tabular-nums">
          {new Date(alert.timestamp).toLocaleTimeString("fr-FR", {
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit",
          })}
        </span>
      </div>
    </div>
  );
}
