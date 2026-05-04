export type CandidateSignal =
  | "promotional_digest"
  | "recurring_updates"
  | "ambiguous_source";

export type CandidateState =
  | "pending_review"
  | "kept"
  | "marked_low_value"
  | "action_recommended";

export type DecisionValue =
  | "keep_for_now"
  | "mark_low_value"
  | "unsubscribe_later";

export interface PaginationMeta {
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
  has_previous: boolean;
  has_next: boolean;
}

export interface SourceRow {
  id: number;
  source_key: string;
  source_name: string;
  sender_emails: string[];
  sender_domain?: string | null;
  email_count: number;
  representative_subject: string;
  representative_message_id?: string | null;
  representative_message_timestamp?: string | null;
  representative_label_ids?: string[] | null;
  representative_list_id?: string | null;
  has_list_unsubscribe?: boolean | null;
  mailbox_category: string;
  candidate_reason: string;
  classifier_signal: CandidateSignal;
  suggested_decision: DecisionValue;
  current_decision: DecisionValue | null;
  confidence: number | null;
  processing_state: CandidateState;
}

export interface SourceSummary {
  id: number;
  source_key: string;
  source_name: string;
  sender_emails: string[];
  email_count: number;
  representative_subject: string;
  mailbox_category: string;
  current_decision: DecisionValue | null;
  processing_state: CandidateState;
}

export interface DecisionRecord {
  id: number;
  revised_from_decision_id: number | null;
  decision: DecisionValue;
  note: string | null;
  human_confirmed: boolean;
  external_action_status: "not_executed";
  created_at: string;
  is_current: boolean;
  is_revision: boolean;
  source: SourceSummary;
}

export interface SourceListResponse {
  items: SourceRow[];
  pagination: PaginationMeta;
  available_categories: string[];
}

export interface DecisionListResponse {
  items: DecisionRecord[];
  pagination: PaginationMeta;
}

export interface DecisionCreateRequest {
  source_id: number;
  decision: DecisionValue;
  confirmed: boolean;
  note?: string;
}

export interface BatchDecisionCreateRequest {
  source_ids: number[];
  decision: DecisionValue;
  confirmed: boolean;
  note?: string;
}

export interface BatchDecisionResponse {
  applied: DecisionRecord[];
  unchanged: DecisionRecord[];
}

export const signalLabels: Record<CandidateSignal, string> = {
  promotional_digest: "Promotional digest",
  recurring_updates: "Recurring updates",
  ambiguous_source: "Ambiguous source",
};

export const processingStateLabels: Record<CandidateState, string> = {
  pending_review: "Pending review",
  kept: "Keep Source",
  marked_low_value: "Mark as Low Value",
  action_recommended: "Queue for Unsubscribe",
};

export const decisionActionLabels: Record<DecisionValue, string> = {
  keep_for_now: "Keep Source",
  mark_low_value: "Mark as Low Value",
  unsubscribe_later: "Queue for Unsubscribe",
};

export const decisionHistoryLabels: Record<DecisionValue, string> = {
  keep_for_now: "Keep Source",
  mark_low_value: "Mark as Low Value",
  unsubscribe_later: "Queue for Unsubscribe",
};
