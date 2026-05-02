export type WorkflowStageKey = "connect" | "review" | "decide" | "complete";

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
