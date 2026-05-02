export type WorkflowStageKey = "connect" | "review" | "decide" | "complete";

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

export interface Candidate {
  id: number;
  sender_name: string;
  sender_email: string;
  subject: string;
  mailbox_category: string;
  candidate_reason: string;
  classifier_signal: CandidateSignal;
  suggested_decision: DecisionValue;
  confidence: number | null;
  processing_state: CandidateState;
}

export interface CandidateSummary {
  id: number;
  sender_name: string;
  sender_email: string;
  subject: string;
  processing_state: CandidateState;
}

export interface DecisionRecord {
  id: number;
  decision: DecisionValue;
  note: string | null;
  human_confirmed: boolean;
  external_action_status: "not_executed";
  created_at: string;
  candidate: CandidateSummary;
}

export interface CandidateListResponse {
  items: Candidate[];
}

export interface DecisionListResponse {
  items: DecisionRecord[];
}

export interface DecisionCreateRequest {
  candidate_id: number;
  decision: DecisionValue;
  confirmed: boolean;
  note?: string;
}

export interface WorkflowStage {
  key: WorkflowStageKey;
  label: string;
  summary: string;
}

export const workflowStages: WorkflowStage[] = [
  {
    key: "connect",
    label: "Connect",
    summary:
      "Prepare for a future Gmail connection without implementing OAuth in this slice.",
  },
  {
    key: "review",
    label: "Review Candidates",
    summary:
      "Surface a bounded set of likely low-value messages once ingestion exists.",
  },
  {
    key: "decide",
    label: "Decide",
    summary:
      "Keep the user in the loop for every decision that affects email state.",
  },
  {
    key: "complete",
    label: "Complete",
    summary:
      "Persist processed state locally before any later action automation is considered.",
  },
];

export const signalLabels: Record<CandidateSignal, string> = {
  promotional_digest: "Promotional digest",
  recurring_updates: "Recurring updates",
  ambiguous_source: "Ambiguous source",
};

export const processingStateLabels: Record<CandidateState, string> = {
  pending_review: "Pending review",
  kept: "Kept for now",
  marked_low_value: "Marked low value",
  action_recommended: "Action recommended",
};

export const decisionActionLabels: Record<DecisionValue, string> = {
  keep_for_now: "Keep For Now",
  mark_low_value: "Mark Low Value",
  unsubscribe_later: "Recommend Unsubscribe Later",
};

export const decisionHistoryLabels: Record<DecisionValue, string> = {
  keep_for_now: "Kept for now",
  mark_low_value: "Marked as low value",
  unsubscribe_later: "Recommended for later unsubscribe",
};
