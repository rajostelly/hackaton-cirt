import { useQuery } from "@tanstack/react-query";
import { Plug2, RefreshCw, Wifi, WifiOff, ExternalLink } from "lucide-react";
import apiClient from "@/api/client";

type IntStatus = "active" | "configured" | "inactive" | "error";
type Category = "siem" | "threat-intel" | "endpoint" | "network";

interface Integration {
  id: string;
  name: string;
  description: string;
  category: Category;
  status: IntStatus;
  envVar: string;
  port?: string;
}

const INTEGRATIONS: Integration[] = [
  {
    id: "wazuh-manager",
    name: "Wazuh Manager",
    description:
      "Gestionnaire central SIEM/XDR — collecte, corrèle et analyse les événements de sécurité.",
    category: "siem",
    status: "active",
    envVar: "WAZUH_MANAGER_URL",
    port: ":55000",
  },
  {
    id: "wazuh-indexer",
    name: "Wazuh Indexer (OpenSearch)",
    description:
      "Moteur d'indexation des logs de sécurité. Dashboard disponible sur le port 443.",
    category: "siem",
    status: "active",
    envVar: "WAZUH_INDEXER_URL",
    port: ":9200",
  },
  {
    id: "virustotal",
    name: "VirusTotal",
    description:
      "Analyse d'IPs, URLs et fichiers via 70+ moteurs antivirus pour la détection de menaces.",
    category: "threat-intel",
    status: "configured",
    envVar: "VIRUSTOTAL_API_KEY",
  },
  {
    id: "crowdstrike",
    name: "CrowdStrike Falcon",
    description:
      "Plateforme EDR cloud-native — détection et réponse sur les endpoints.",
    category: "endpoint",
    status: "inactive",
    envVar: "CROWDSTRIKE_CLIENT_ID + CROWDSTRIKE_CLIENT_SECRET",
  },
  {
    id: "paloalto",
    name: "Palo Alto PAN-OS",
    description:
      "Pare-feu next-gen — contrôle applicatif, IPS et filtrage avancé.",
    category: "network",
    status: "inactive",
    envVar: "PALOALTO_HOST + PALOALTO_API_KEY",
  },
];

const CATEGORY_META: Record<Category, { label: string; description: string }> = {
  siem:          { label: "SIEM / XDR",           description: "Collecte et corrélation des événements" },
  "threat-intel":{ label: "Threat Intelligence",   description: "Enrichissement et renseignement sur les menaces" },
  endpoint:      { label: "Endpoint (EDR)",         description: "Détection et réponse sur les postes" },
  network:       { label: "Réseau (NGFW)",          description: "Protection périmétrique" },
};

export function IntegrationsPage() {
  const { data: health, isLoading: healthLoading } = useQuery({
    queryKey: ["health"],
    queryFn: async () => {
      const { data } = await apiClient.get<{ status: string }>("/health");
      return data;
    },
    refetchInterval: 30_000,
    retry: 1,
  });

  const apiOnline = health?.status === "ok";
  const activeCount = INTEGRATIONS.filter(
    (i) => i.status === "active" || i.status === "configured",
  ).length;

  return (
    <div className="flex flex-col min-h-full">
      {/* Header */}
      <header className="border-b border-gray-800/80 px-6 py-4 shrink-0 flex items-center justify-between">
        <div>
          <h1 className="text-base font-semibold text-white flex items-center gap-2">
            <Plug2 className="w-4 h-4 text-gray-500" />
            Intégrations
          </h1>
          <p className="text-xs text-gray-600 mt-0.5">
            {activeCount}/{INTEGRATIONS.length} connecteurs actifs
          </p>
        </div>
        <div className="flex items-center gap-2">
          {/* API health indicator */}
          <div
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded text-xs ${
              healthLoading
                ? "text-gray-600"
                : apiOnline
                  ? "text-green-400 bg-green-950/30"
                  : "text-red-400 bg-red-950/30"
            }`}
          >
            {apiOnline ? <Wifi className="w-3 h-3" /> : <WifiOff className="w-3 h-3" />}
            {healthLoading ? "…" : apiOnline ? "API en ligne" : "API hors ligne"}
          </div>
          <button className="p-2 text-gray-600 hover:text-gray-300 rounded transition-colors">
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>
      </header>

      <main className="flex-1 p-6 flex flex-col gap-7">
        {(["siem", "threat-intel", "endpoint", "network"] as Category[]).map(
          (cat) => {
            const items = INTEGRATIONS.filter((i) => i.category === cat);
            const meta = CATEGORY_META[cat];
            return (
              <section key={cat}>
                <div className="mb-3">
                  <p className="text-sm font-medium text-gray-300">{meta.label}</p>
                  <p className="text-xs text-gray-600">{meta.description}</p>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {items.map((intg) => (
                    <IntegrationCard key={intg.id} integration={intg} />
                  ))}
                </div>
              </section>
            );
          },
        )}
      </main>
    </div>
  );
}

function IntegrationCard({ integration }: { integration: Integration }) {
  const DOT: Record<IntStatus, string> = {
    active:     "bg-green-500",
    configured: "bg-blue-500",
    inactive:   "bg-gray-700",
    error:      "bg-red-500",
  };
  const LABEL: Record<IntStatus, string> = {
    active:     "Actif",
    configured: "Configuré",
    inactive:   "Non configuré",
    error:      "Erreur",
  };
  const TEXT_CLS: Record<IntStatus, string> = {
    active:     "text-gray-400",
    configured: "text-gray-400",
    inactive:   "text-gray-700",
    error:      "text-red-400",
  };

  const isOperational =
    integration.status === "active" || integration.status === "configured";
  const isPulsing = integration.status === "active";

  return (
    <div className="bg-surface-alt border border-gray-800/80 rounded-lg p-5 flex flex-col gap-4">
      {/* Card header */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2.5">
          {/* Status dot */}
          <div className="relative shrink-0">
            <div className={`w-2 h-2 rounded-full ${DOT[integration.status]}`} />
            {isPulsing && (
              <div
                className={`absolute inset-0 rounded-full ${DOT[integration.status]} animate-ping opacity-50`}
              />
            )}
          </div>
          <div>
            <p className="text-sm font-medium text-white leading-tight">
              {integration.name}
            </p>
            {integration.port && (
              <code className="text-[10px] text-gray-600 font-mono">
                {integration.port}
              </code>
            )}
          </div>
        </div>
        <span className={`text-xs shrink-0 font-medium ${TEXT_CLS[integration.status]}`}>
          {LABEL[integration.status]}
        </span>
      </div>

      {/* Description */}
      <p className="text-xs text-gray-500 leading-relaxed">{integration.description}</p>

      {/* Env var */}
      <div className="bg-surface rounded p-2.5 border border-gray-800/60">
        <p className="text-[10px] text-gray-700 mb-0.5">Variable d'env.</p>
        <code className="text-xs font-mono text-gray-400 break-all">{integration.envVar}</code>
      </div>

      {/* Actions */}
      <div className="flex gap-2">
        <button
          disabled={!isOperational}
          className={`flex-1 py-1.5 text-xs font-medium rounded border transition-colors ${
            isOperational
              ? "border-gray-700 text-gray-400 hover:bg-surface-elevated hover:text-white"
              : "border-gray-800 text-gray-700 cursor-not-allowed"
          }`}
        >
          Tester
        </button>
        <button className="flex items-center justify-center gap-1.5 flex-1 py-1.5 text-xs font-medium rounded border border-gray-700 text-gray-400 hover:bg-surface-elevated hover:text-white transition-colors">
          <ExternalLink className="w-3 h-3" />
          Configurer
        </button>
      </div>
    </div>
  );
}

