import { useState } from "react";
import type { ReactNode } from "react";
import {
  Settings,
  Key,
  Bell,
  Monitor,
  Info,
  ShieldCheck,
  Server,
  Cpu,
  GitBranch,
} from "lucide-react";
import { API_BASE } from "@/api/config";

export function SettingsPage() {
  return (
    <div className="flex flex-col min-h-full">
      {/* Header */}
      <header className="border-b border-gray-800 px-6 py-4 shrink-0">
        <h1 className="text-base font-semibold text-white flex items-center gap-2">
          <Settings className="w-4 h-4 text-gray-500" />
          Paramètres
        </h1>
        <p className="text-xs text-gray-600 mt-0.5">
          Configuration de la plateforme ARO SOC
        </p>
      </header>

      <main className="flex-1 p-6">
        <div className="max-w-2xl flex flex-col gap-8">
          {/* API Config */}
          <Section title="Configuration API" icon={<Key className="w-4 h-4" />}>
            <SettingRow
              label="Endpoint de l'API"
              description="URL du backend FastAPI (proxy Vite en développement)"
              value={API_BASE}
              mono
              readonly
            />
            <SettingRow
              label="Intervalle de rafraîchissement"
              description="Fréquence de mise à jour automatique des alertes"
              value="5 secondes"
              readonly
            />
            <SettingRow
              label="Limite par requête"
              description="Nombre maximum d'alertes chargées par appel API"
              value="100 alertes"
              readonly
            />
          </Section>

          {/* Notifications */}
          <Section title="Notifications" icon={<Bell className="w-4 h-4" />}>
            <SettingToggle
              label="Toasts temps réel"
              description="Afficher les notifications lors de la détection d'un scan nmap"
              defaultEnabled
            />
            <SettingToggle
              label="Son d'alerte"
              description="Émettre un bip sonore lors d'une alerte de criticité critique"
              defaultEnabled={false}
            />
            <SettingToggle
              label="Mise en évidence urgente"
              description="Afficher un badge URGENT sur les alertes critiques non triées"
              defaultEnabled
            />
          </Section>

          {/* Display */}
          <Section title="Affichage" icon={<Monitor className="w-4 h-4" />}>
            <SettingToggle
              label="Thème sombre"
              description="Interface optimisée pour les environnements SOC basse luminosité"
              defaultEnabled
              locked
            />
            <SettingToggle
              label="Sidebar réduite par défaut"
              description="Démarrer avec la barre de navigation en mode icônes uniquement"
              defaultEnabled={false}
            />
            <SettingToggle
              label="Nombres tabulaires"
              description="Alignement fixe des chiffres dans les compteurs et tableaux"
              defaultEnabled
            />
          </Section>

          {/* À propos */}
          <Section title="À propos" icon={<Info className="w-4 h-4" />}>
            <div className="p-4 grid grid-cols-2 gap-4 text-sm">
              <AboutField
                icon={<ShieldCheck className="w-4 h-4 text-blue-400" />}
                label="Plateforme"
                value="ARO Security Operations Center"
              />
              <AboutField
                icon={<GitBranch className="w-4 h-4 text-gray-400" />}
                label="Version"
                value="1.0.0 · Hackathon Edition"
              />
              <AboutField
                icon={<Server className="w-4 h-4 text-gray-400" />}
                label="Backend"
                value="FastAPI · Python 3.12 · Groq llama-3.3-70b"
              />
              <AboutField
                icon={<Cpu className="w-4 h-4 text-gray-400" />}
                label="Frontend"
                value="React 19 · Vite · Tailwind CSS v4"
              />
              <AboutField
                icon={<Monitor className="w-4 h-4 text-gray-400" />}
                label="SIEM"
                value="Wazuh 4.x · OpenSearch"
              />
              <AboutField
                icon={<Bell className="w-4 h-4 text-gray-400" />}
                label="Détection réseau"
                value="Scapy SYN-scan detector · sfyrisec.duckdns.org"
              />
            </div>
          </Section>

          {/* Danger zone */}
          <Section
            title="Zone de danger"
            icon={<Settings className="w-4 h-4 text-red-500" />}
            headerClass="text-red-400"
          >
            <div className="p-4 flex items-center justify-between gap-4">
              <div>
                <p className="text-sm font-medium text-white">
                  Vider le cache des alertes
                </p>
                <p className="text-xs text-gray-500 mt-0.5">
                  Force un rechargement complet depuis l'API
                </p>
              </div>
              <button className="px-4 py-1.5 text-xs font-medium rounded-md border border-gray-700 text-gray-300 hover:bg-surface-elevated hover:text-white transition-colors">
                Vider le cache
              </button>
            </div>
          </Section>
        </div>
      </main>
    </div>
  );
}

/* ── Section wrapper ── */
function Section({
  title,
  icon,
  children,
  headerClass = "text-white",
}: {
  title: string;
  icon: ReactNode;
  children: ReactNode;
  headerClass?: string;
}) {
  return (
    <div>
      <h2
        className={`text-sm font-semibold flex items-center gap-2 mb-3 ${headerClass}`}
      >
        <span className="text-gray-500">{icon}</span>
        {title}
      </h2>
      <div className="bg-surface-alt border border-gray-800 rounded-lg divide-y divide-gray-800">
        {children}
      </div>
    </div>
  );
}

/* ── Setting row (readonly or input) ── */
function SettingRow({
  label,
  description,
  value,
  mono,
  readonly,
}: {
  label: string;
  description: string;
  value: string;
  mono?: boolean;
  readonly?: boolean;
}) {
  return (
    <div className="px-5 py-4 flex items-center justify-between gap-6">
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-white">{label}</p>
        <p className="text-xs text-gray-500 mt-0.5">{description}</p>
      </div>
      {readonly ? (
        <span
          className={`text-xs shrink-0 bg-surface-elevated border border-gray-800 px-2.5 py-1 rounded text-gray-400 ${
            mono ? "font-mono" : ""
          }`}
        >
          {value}
        </span>
      ) : (
        <input
          type="text"
          defaultValue={value}
          className="w-40 text-sm bg-surface-elevated border border-gray-700 rounded-md px-3 py-1.5 text-white focus:outline-none focus:border-blue-600 transition-colors shrink-0"
        />
      )}
    </div>
  );
}

/* ── Toggle setting ── */
function SettingToggle({
  label,
  description,
  defaultEnabled,
  locked,
}: {
  label: string;
  description: string;
  defaultEnabled: boolean;
  locked?: boolean;
}) {
  const [enabled, setEnabled] = useState(defaultEnabled);

  return (
    <div className="px-5 py-4 flex items-center justify-between gap-6">
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-white">{label}</p>
        <p className="text-xs text-gray-500 mt-0.5">{description}</p>
      </div>
      <button
        onClick={() => !locked && setEnabled((e) => !e)}
        className={`relative inline-flex h-6 w-11 shrink-0 items-center rounded-full transition-colors ${
          enabled ? "bg-blue-600" : "bg-gray-700"
        } ${locked ? "opacity-40 cursor-not-allowed" : "cursor-pointer"}`}
        aria-label={label}
        aria-pressed={enabled}
      >
        <span
          className={`inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform ${
            enabled ? "translate-x-6" : "translate-x-1"
          }`}
        />
      </button>
    </div>
  );
}

/* ── About field ── */
function AboutField({
  icon,
  label,
  value,
}: {
  icon: ReactNode;
  label: string;
  value: string;
}) {
  return (
    <div className="flex items-start gap-2.5">
      <div className="mt-0.5 shrink-0">{icon}</div>
      <div>
        <p className="text-xs text-gray-500 mb-0.5">{label}</p>
        <p className="text-sm text-white font-medium leading-snug">{value}</p>
      </div>
    </div>
  );
}
