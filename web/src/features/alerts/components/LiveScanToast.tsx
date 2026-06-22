import { useEffect } from "react";
import type { AlertOut } from "@/api/types";
import { CriticityBadge } from "@/shared/ui/Badge";

const AUTO_DISMISS_MS = 12_000;

interface LiveScanToastProps {
  alert: AlertOut;
  onDismiss: () => void;
}

export function LiveScanToast({ alert, onDismiss }: LiveScanToastProps) {
  useEffect(() => {
    const timer = setTimeout(onDismiss, AUTO_DISMISS_MS);
    return () => clearTimeout(timer);
  }, [onDismiss]);

  return (
    <div className="w-80 bg-surface-alt border border-red-700/60 rounded-lg shadow-xl p-4 flex flex-col gap-2 animate-[pulse_1.5s_ease-in-out_1]">
      <div className="flex items-center justify-between gap-2">
        <span className="flex items-center gap-2 text-red-400 font-semibold text-sm">
          <span className="w-2 h-2 rounded-full bg-red-500 inline-block animate-pulse" />
          Scan détecté
        </span>
        <button
          onClick={onDismiss}
          className="text-gray-500 hover:text-white text-lg leading-none"
          aria-label="Fermer"
        >
          ×
        </button>
      </div>
      <p className="text-sm text-white font-medium leading-snug">{alert.title}</p>
      <div className="flex items-center justify-between">
        <span className="font-mono text-xs text-gray-400">{alert.source_ip}</span>
        <CriticityBadge criticity={alert.criticity} />
      </div>
    </div>
  );
}
