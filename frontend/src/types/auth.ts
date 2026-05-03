export interface UserMe {
  id: number;
  email: string | null;
  display_name: string;
  is_local_alpha: boolean;
}

export type ConnectionStatus =
  | "connected"
  | "disconnected"
  | "expired"
  | "revoked"
  | "error"
  | "local_only";

export interface EmailAccountInfo {
  id: number;
  provider: "gmail" | "microsoft" | "imap" | "local_alpha";
  account_email: string;
  display_name: string;
  connection_status: ConnectionStatus;
  granted_scopes: string[];
}

export interface IngestionRunSummary {
  id: number;
  status: "pending" | "running" | "completed" | "failed" | "cancelled";
  scope: string | null;
  limit_count: number | null;
  message_count_scanned: number;
  source_count_created: number;
  error_summary: string | null;
  started_at: string | null;
  completed_at: string | null;
}
