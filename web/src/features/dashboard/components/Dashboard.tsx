import { useState } from "react";
import { useNavigate } from "react-router-dom";
import type { ReactNode } from "react";
import {
  AlertTriangle,
  ArrowRight,
  RefreshCw,
  Wifi,
  WifiOff,
} from "lucide-react";
import type { AlertOut } from "@/api/types";
import { CriticityBadge } from "@/shared/ui/Badge";
import { LiveScanToast } from "@/features/alerts/components/LiveScanToast";
import { useOpenAlerts } from "@/features/alerts/hooks/useAlerts";
import { useAlertStream } from "@/features/alerts/hooks/useAlertStream";

export function Dashboard() {
  const navigate = useNavigate();
  const [liveScans, setLiveScans] = useState<AlertOut[]>([]);
  const { data: alerts = [], isLoading, error, refetch } = useOpenAlerts();

  const { status: streamStatus } = useAlertStream((event) => {
    if (event.type === "alert.created") {
      setLiveScans((prev) => [event.data, ...prev].slice(0, 4));
    }
  });

  const isLive = streamStatus === "open";

  const critical = alerts.filter((a) => a.criticity === "critical").length;
  const high     = alerts.filter((a) => a.criticity === "high").length;
  const medium   = alerts.filter((a) => a.criticity === "medium").length;
  const low      = alerts.filter((a) => a.criticity === "low").length;
  const scans    = alerts.filter(
    (a) =>
      a.rule_name.toLowerCase().includes("scan") ||
      a.title.toLowerCase().includes("scan") ||
      a.title.toLowerCase().includes("nmap"),
  ).length;

  const recent = [...alerts]
    .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
    .slice(0, 6);

  return (
    <div className="flex flex-col min-h-full">
      {/* Header */}
      <header className="border-b border-gray-800/80 px-6 py-4 flex items-center justify-between shrink-0">
        <div>
          <h1 className="text-base font-semibold text-white">Vue d'ensemble</h1>
          <p className="text-xs text-gray-600 mt-0.5">Tableau de bord opérationnel</p>
        </div>
        <div className="flex items-center gap-2">
          <StreamBadge isLive={isLive} />
          <button
            onClick={() => void refetch()}
            className="p-2 text-gray-600 hover:text-gray-300 rounded transition-colors"
            aria-label="Rafraîchir"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>
      </header>

      <main className="flex-1 p-6 flex flex-col gap-5">
        {/* Loading */}
        {isLoading && (
          <div className="flex items-center justify-center py-20">
            <div className="w-6 h-6 border-2 border-gray-800 border-t-blue-500 rounded-full animate-spin" />
          </div>
        )}

        {/* Error */}
        {error && !isLoading && (
          <div className="flex items-center gap-3 bg-red-950/20 border border-red-900/40 rounded-lg p-4 text-sm text-red-400">
            <AlertTriangle className="w-4 h-4 shrink-0" />
            Backend non accessible — démarrez l'API sur le port 8000.
          </div>
        )}

        {!isLoading && !error && (
          <>
            {/* KPI grid — uniform neutral cards */}
            <div className="grid grid-cols-2 xl:grid-cols-4 gap-3">
              <StatCard
                label="Total alertes"
                value={alerts.length}
                sub="Toutes criticités"
                onClick={() => navigate("/alerts")}
              />
              <StatCard
                label="Critiques"
                value={critical}
                sub="Intervention immédiate"
                urgent={critical > 0}
                onClick={() => navigate("/alerts?criticity=critical")}
              />
              <StatCard
                label="Élevées"
                value={high}
                sub="Priorité haute"
                onClick={() => navigate("/alerts?criticity=high")}
              />
              <StatCard
                label="Scans réseau"
                value={scans}
                sub="Détectés par capteur"
                onClick={() => navigate("/scans")}
              />
            </div>

            <div className="grid grid-cols-3 gap-3">
              <StatCard
                label="Moyennes"
                value={medium}
                sub="À surveiller"
                onClick={() => navigate("/alerts?criticity=medium")}
              />
              <StatCard
                label="Faibles"
                value={low}
                sub="Faible priorité"
                onClick={() => navigate("/alerts?criticity=low")}
              />
              <StatCard
                label="En attente de triage"
                value={alerts.filter((a) => a.status === "open").length}
                sub="Alertes non triées"
                onClick={() => navigate("/alerts")}
              />
            </div>

            {/* Content */}
            <div className="grid grid-cols-1 xl:grid-cols-3 gap-5">
              {/* Recent alerts */}
              <div className="xl:col-span-2 bg-surface-alt border border-gray-800/80 rounded-lg overflow-hidden">
                <SectionHeader
                  title="Alertes récentes"
                  action={{ label: "Voir toutes", onClick: () => navigate("/alerts") }}
                />
                {recent.length === 0 ? (
                  <div className="py-12 text-center text-sm text-gray-600">
                    Aucune alerte enregistrée
                  </div>
                ) : (
                  <div className="divide-y divide-gray-800/50">
                    {recent.map((a) => (
                      <div
                        key={a.id}
                        onClick={() => navigate("/alerts")}
                        className="px-5 py-3 flex items-center gap-3 hover:bg-surface-elevated cursor-pointer transition-colors"
                      >
                        <CriticityBadge criticity={a.criticity} />
                        <span className="text-sm text-gray-200 flex-1 truncate min-w-0">
                          {a.title}
                        </span>
                        <span className="text-xs font-mono text-gray-600 shrink-0">
                          {a.source_ip}
                        </span>
                        <span className="text-xs text-gray-700 shrink-0 tabular-nums">
                          {new Date(a.timestamp).toLocaleTimeString("fr-FR", {
                            hour: "2-digit",
                            minute: "2-digit",
                          })}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Right column */}
              <div className="flex flex-col gap-5">
                {/* Integrations */}
                <div className="bg-surface-alt border border-gray-800/80 rounded-lg overflow-hidden">
                  <SectionHeader
                    title="Intégrations"
                    action={{
                      label: "Détails",
                      onClick: () => navigate("/integrations"),
                    }}
                  />
                  <div className="p-4 flex flex-col gap-2.5">
                    <IntegLine name="Wazuh Manager"  status="active" />
                    <IntegLine name="Wazuh Indexer"  status="active" />
                    <IntegLine name="VirusTotal"     status="configured" />
                    <IntegLine name="CrowdStrike"    status="inactive" />
                    <IntegLine name="Palo Alto"      status="inactive" />
                  </div>
                </div>

                {/* Stream status */}
                <div className="bg-surface-alt border border-gray-800/80 rounded-lg p-4">
                  <p className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-3">
                    Capteur réseau
                  </p>
                  <div className="flex items-center gap-3 mb-3">
                    <div
                      className={`w-2 h-2 rounded-full shrink-0 ${
                        isLive ? "bg-green-500 animate-pulse" : "bg-gray-700"
                      }`}
                    />
                    <span
                      className={`text-sm font-medium ${
                        isLive ? "text-white" : "text-gray-600"
                      }`}
                    >
                      {isLive ? "Capteur actif" : "Hors ligne"}
                    </span>
                  </div>
                  <button
                    onClick={() => navigate("/scans")}
                    className="w-full text-xs text-gray-500 hover:text-gray-300 border border-gray-800 hover:border-gray-700 rounded-md py-2 transition-colors"
                  >
                    Voir les détections →
                  </button>
                </div>
              </div>
            </div>
          </>
        )}
      </main>

      {/* Toasts */}
      <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-3">
        {liveScans.map((scan) => (
          <LiveScanToast
            key={scan.id}
            alert={scan}
            onDismiss={() =>
              setLiveScans((prev) => prev.filter((s) => s.id !== scan.id))
            }
          />
        ))}
      </div>
    </div>
  );
}

/* ── Uniform neutral stat card ── */
function StatCard({
  label,
  value,
  sub,
  urgent,
  onClick,
}: {
  label: string;
  value: number;
  sub: string;
  urgent?: boolean;
  onClick: () => void;
}) {
  return (
    <div
      onClick={onClick}
      className="bg-surface-alt border border-gray-800/80 rounded-lg p-5 cursor-pointer hover:bg-surface-elevated hover:border-gray-700 transition-all group"
    >
      <div className="flex items-start justify-between">
        <span className="text-3xl font-bold text-white tabular-nums">{value}</span>
        <ArrowRight className="w-3.5 h-3.5 text-gray-700 group-hover:text-gray-400 transition-colors mt-1.5" />
      </div>
      <p className="text-sm text-gray-300 mt-2 font-medium">{label}</p>
      <p className="text-xs text-gray-600 mt-0.5 flex items-center gap-1.5">
        {urgent && value > 0 && (
          <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse shrink-0" />
        )}
        {sub}
      </p>
    </div>
  );
}

/* ── Section header ── */
function SectionHeader({
  title,
  action,
}: {
  title: string;
  action?: { label: string; onClick: () => void };
}) {
  return (
    <div className="px-5 py-3 border-b border-gray-800/60 flex items-center justify-between">
      <p className="text-sm font-medium text-gray-300">{title}</p>
      {action && (
        <button
          onClick={action.onClick}
          className="flex items-center gap-1 text-xs text-gray-600 hover:text-blue-400 transition-colors"
        >
          {action.label} <ArrowRight className="w-3 h-3" />
        </button>
      )}
    </div>
  );
}

/* ── Integration status row ── */
type IntStatus = "active" | "configured" | "inactive" | "error";

function IntegLine({ name, status }: { name: string; status: IntStatus }) {
  const dot: Record<IntStatus, string> = {
    active:     "bg-green-500",
    configured: "bg-blue-500",
    inactive:   "bg-gray-700",
    error:      "bg-red-500",
  };
  const label: Record<IntStatus, string> = {
    active:     "Actif",
    configured: "Configuré",
    inactive:   "—",
    error:      "Erreur",
  };
  const textCls: Record<IntStatus, string> = {
    active:     "text-gray-500",
    configured: "text-gray-500",
    inactive:   "text-gray-700",
    error:      "text-red-400",
  };

  return (
    <div className="flex items-center gap-2.5">
      <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${dot[status]}`} />
      <span className="text-sm text-gray-400 flex-1 truncate">{name}</span>
      <span className={`text-xs ${textCls[status]}`}>{label[status]}</span>
    </div>
  );
}

/* ── Stream badge ── */
function StreamBadge({ isLive }: { isLive: boolean }): ReactNode {
  return (
    <div
      className={`flex items-center gap-1.5 px-2.5 py-1 rounded text-xs ${
        isLive
          ? "text-green-400 bg-green-950/30"
          : "text-gray-600 bg-gray-900/50"
      }`}
    >
      {isLive ? <Wifi className="w-3 h-3" /> : <WifiOff className="w-3 h-3" />}
      {isLive ? "Live" : "Offline"}
    </div>
  );
}
