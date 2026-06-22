export type Criticity = "low" | "medium" | "high" | "critical";
export type AlertStatus = "open" | "triaged" | "closed";

export interface AlertIn {
  title: string;
  source_ip: string;
  destination_ip?: string | null;
  criticity: Criticity;
  rule_name: string;
  raw_data?: Record<string, unknown> | null;
}

export interface AlertOut {
  id: string;
  title: string;
  source_ip: string;
  destination_ip?: string | null;
  criticity: Criticity;
  rule_name: string;
  status: AlertStatus;
  timestamp: string;
  explanation?: string | null;
  is_false_positive?: boolean | null;
}

export interface TriageIn {
  is_false_positive: boolean;
  analyst_note?: string | null;
}

export interface HealthResponse {
  status: "ok";
}
