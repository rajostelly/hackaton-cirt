import { useEffect, useRef, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { API_BASE } from "@/api/config";
import type { AlertOut } from "@/api/types";

export type StreamStatus = "connecting" | "open" | "error";

export interface AlertStreamEvent {
  type: "alert.created" | "alert.updated";
  data: AlertOut;
}

// Flux SSE temps réel des alertes (scans nmap détectés par le capteur).
// https://developer.mozilla.org/en-US/docs/Web/API/EventSource
export function useAlertStream(onEvent?: (event: AlertStreamEvent) => void) {
  const queryClient = useQueryClient();
  const [status, setStatus] = useState<StreamStatus>("connecting");
  const onEventRef = useRef(onEvent);

  useEffect(() => {
    onEventRef.current = onEvent;
  });

  useEffect(() => {
    const source = new EventSource(`${API_BASE}/stream/alerts`);

    source.onopen = () => setStatus("open");
    source.onerror = () => setStatus("error");
    source.onmessage = (message) => {
      let event: AlertStreamEvent;
      try {
        event = JSON.parse(message.data) as AlertStreamEvent;
      } catch {
        return; // commentaires de heartbeat / lignes non-JSON
      }
      // Rafraîchit instantanément les listes/compteurs d'alertes.
      queryClient.invalidateQueries({ queryKey: ["alerts"] });
      onEventRef.current?.(event);
    };

    return () => source.close();
  }, [queryClient]);

  return { status };
}
