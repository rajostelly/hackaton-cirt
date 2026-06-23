import { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { Bell, Search, RefreshCw, Wifi, WifiOff, X } from "lucide-react";
import type { AlertOut, Criticity } from "@/api/types";
import { AlertList } from "./AlertList";
import { AlertDetail } from "./AlertDetail";
import { LiveScanToast } from "./LiveScanToast";
import { useOpenAlerts } from "../hooks/useAlerts";
import { useAlertStream } from "../hooks/useAlertStream";

const TABS: { value: Criticity | null; label: string }[] = [
  { value: null, label: "Toutes" },
  { value: "critical", label: "Critiques" },
  { value: "high", label: "Élevées" },
  { value: "medium", label: "Moyennes" },
  { value: "low", label: "Faibles" },
];

export function AlertsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const urlCriticity = searchParams.get("criticity") as Criticity | null;

  // Filter state — applied client-side so all tab counts stay accurate
  const [criticity, setCriticity] = useState<Criticity | null>(
    urlCriticity,
  );
  const [search, setSearch] = useState("");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [liveScans, setLiveScans] = useState<AlertOut[]>([]);

  // Always fetch all alerts; filter client-side
  const {
    data: allAlerts = [],
    isLoading,
    error,
    refetch,
  } = useOpenAlerts();

  const { status: streamStatus } = useAlertStream((event) => {
    if (event.type === "alert.created") {
      setLiveScans((prev) => [event.data, ...prev].slice(0, 4));
    }
  });

  const isLive = streamStatus === "open";

  // Sync criticity → URL
  useEffect(() => {
    if (criticity) {
      setSearchParams({ criticity });
    } else {
      setSearchParams({});
    }
  }, [criticity, setSearchParams]);

  // Client-side filtering
  const byCriticity = criticity
    ? allAlerts.filter((a) => a.criticity === criticity)
    : allAlerts;

  const filtered = search.trim()
    ? byCriticity.filter(
        (a) =>
          a.title.toLowerCase().includes(search.toLowerCase()) ||
          a.source_ip.includes(search) ||
          a.rule_name.toLowerCase().includes(search.toLowerCase()),
      )
    : byCriticity;

  const selectedAlert = filtered.find((a) => a.id === selectedId);

  function handleCriticityChange(value: Criticity | null) {
    setCriticity(value);
    setSelectedId(null);
  }

  return (
    <div className="flex flex-col min-h-full">
      {/* Page header */}
      <header className="border-b border-gray-800 px-6 py-4 shrink-0">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-base font-semibold text-white flex items-center gap-2">
              <Bell className="w-4 h-4 text-gray-500" />
              Alertes
              {!isLoading && (
                <span className="text-xs font-normal text-gray-600 ml-0.5">
                  ({filtered.length}
                  {search || criticity ? ` / ${allAlerts.length}` : ""})
                </span>
              )}
            </h1>
            <p className="text-xs text-gray-600 mt-0.5">
              Gestion et triage des alertes de sécurité
            </p>
          </div>

          <div className="flex items-center gap-3">
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
            <button
              onClick={() => void refetch()}
              className="text-gray-500 hover:text-white p-2 rounded-md hover:bg-surface-elevated transition-colors"
              aria-label="Rafraîchir"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Filter bar */}
        <div className="flex items-center gap-3 flex-wrap">
          {/* Criticality tabs */}
          <div className="flex bg-surface-elevated rounded-lg p-0.5 border border-gray-800">
            {TABS.map(({ value, label }) => {
              const isActive = criticity === value;
              const count =
                value !== null
                  ? allAlerts.filter((a) => a.criticity === value).length
                  : null;
              return (
                <button
                  key={value ?? "all"}
                  onClick={() => handleCriticityChange(value)}
                  className={`px-3 py-1.5 text-xs font-medium rounded transition-colors ${
                    isActive
                      ? "bg-gray-700 text-white"
                      : "text-gray-500 hover:text-gray-300"
                  }`}
                >
                  {label}
                  {!isLoading && count !== null && (
                    <span
                      className={`ml-1.5 tabular-nums ${
                        isActive ? "text-gray-400" : "text-gray-700"
                      }`}
                    >
                      {count}
                    </span>
                  )}
                </button>
              );
            })}
          </div>

          {/* Search */}
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-600" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="IP, titre, règle…"
              className="w-full pl-9 pr-9 py-1.5 text-sm bg-surface-elevated border border-gray-800 rounded-lg text-white placeholder-gray-600 focus:outline-none focus:border-gray-600 transition-colors"
            />
            {search && (
              <button
                onClick={() => setSearch("")}
                className="absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-600 hover:text-gray-400"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1 p-6">
        {isLoading && (
          <div className="flex items-center justify-center py-20">
            <div className="w-7 h-7 border-2 border-gray-700 border-t-blue-500 rounded-full animate-spin" />
          </div>
        )}

        {error && !isLoading && (
          <div className="bg-red-950/30 border border-red-800/40 rounded-lg p-4 text-sm text-red-400">
            Erreur de connexion à l'API — vérifiez que le backend est démarré.
          </div>
        )}

        {!isLoading && !error && (
          <div
            className={selectedAlert ? "grid gap-5 items-start" : "block"}
            style={
              selectedAlert
                ? { gridTemplateColumns: "1fr 380px" }
                : undefined
            }
          >
            <AlertList
              alerts={filtered}
              selectedId={selectedId}
              onSelect={(id) =>
                setSelectedId((prev) => (prev === id ? null : id))
              }
            />
            {selectedAlert && (
              <div className="sticky top-0">
                <AlertDetail
                  alert={selectedAlert}
                  onClose={() => setSelectedId(null)}
                />
              </div>
            )}
          </div>
        )}
      </main>

      {/* Live toasts */}
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
