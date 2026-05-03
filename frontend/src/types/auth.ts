export interface UserMe {
  id: number;
  email: string | null;
  display_name: string;
  is_local_alpha: boolean;
}

export type AuthMode = "google_oauth" | "local_dev";

export interface AuthConfig {
  auth_mode: AuthMode;
  local_dev_enabled: boolean;
  google_oauth_enabled: boolean;
  google_oauth_message: string | null;
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
  source_count_seen: number;
  source_count_created: number;
  error_summary: string | null;
  started_at: string | null;
  completed_at: string | null;
}

export type ResetLocalDataMode = "sources_only" | "sources_and_decisions";

export interface ResetLocalDataSummary {
  account_id: number;
  account_email: string;
  mode: ResetLocalDataMode;
  sources_deleted: number;
  decisions_deleted: number;
  ingestion_runs_preserved: number;
  ingestion_runs_deleted: number;
}
