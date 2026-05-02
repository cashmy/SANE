import { useEffect, useState } from "react";

import { createDecision, listCandidates, listDecisions } from "../services/api";
import {
  decisionActionLabels,
  decisionHistoryLabels,
  processingStateLabels,
  signalLabels,
  workflowStages,
  type Candidate,
  type DecisionRecord,
  type DecisionValue,
} from "../types/workflow";

const formatConfidence = (confidence: number | null) => {
  if (confidence === null) {
    return "Manual review weight only";
  }

  return `${Math.round(confidence * 100)}% heuristic confidence`;
};

const formatDecisionTimestamp = (value: string) => {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "Recorded locally";
  }

  return new Intl.DateTimeFormat("en", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
};

const toErrorMessage = (error: unknown) => {
  if (error instanceof Error) {
    return error.message;
  }

  return "The ALPHA review queue could not be loaded.";
};

export function WorkflowBoard() {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [decisions, setDecisions] = useState<DecisionRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [submittingCandidateId, setSubmittingCandidateId] = useState<
    number | null
  >(null);

  const loadWorkflow = async () => {
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const [candidateResponse, decisionResponse] = await Promise.all([
        listCandidates(),
        listDecisions(),
      ]);

      setCandidates(candidateResponse.items);
      setDecisions(decisionResponse.items);
    } catch (error) {
      setErrorMessage(toErrorMessage(error));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    void loadWorkflow();
  }, []);

  const handleDecision = async (
    candidateId: number,
    decision: DecisionValue,
  ) => {
    setSubmittingCandidateId(candidateId);
    setErrorMessage(null);

    try {
      const createdDecision = await createDecision({
        candidate_id: candidateId,
        decision,
        confirmed: true,
      });

      setCandidates((current) =>
        current.filter(
          (candidate) => candidate.id !== createdDecision.candidate.id,
        ),
      );
      setDecisions((current) => [createdDecision, ...current]);
    } catch (error) {
      setErrorMessage(toErrorMessage(error));
    } finally {
      setSubmittingCandidateId(null);
    }
  };

  return (
    <section className="workflow-board" aria-labelledby="workflow-title">
      <header className="panel intro">
        <div className="intro-copy">
          <p className="eyebrow">Stage 1 ALPHA candidate</p>
          <h1 id="workflow-title">
            Review likely low-value email sources without executing email
            actions.
          </h1>
          <p className="summary">
            This pass uses deterministic demo candidates and local persistence
            to prove the decision loop. Gmail access, OAuth, and external
            actions remain deferred.
          </p>
        </div>

        <dl className="status-strip" aria-label="Workflow status summary">
          <div>
            <dt>Pending review</dt>
            <dd>{candidates.length}</dd>
          </div>
          <div>
            <dt>Recorded locally</dt>
            <dd>{decisions.length}</dd>
          </div>
          <div>
            <dt>External actions</dt>
            <dd>Not executed</dd>
          </div>
        </dl>
      </header>

      <section className="panel stages" aria-labelledby="stages-title">
        <div className="section-header">
          <div>
            <p className="eyebrow">Decision loop</p>
            <h2 id="stages-title">Identify - Decide - Act - Complete</h2>
          </div>
          <button
            className="refresh-button"
            type="button"
            onClick={() => {
              void loadWorkflow();
            }}
            disabled={isLoading || submittingCandidateId !== null}
          >
            Refresh local state
          </button>
        </div>
        <ol className="stage-grid">
          {workflowStages.map((stage, index) => (
            <li className="stage-card" key={stage.key}>
              <span className="stage-index">0{index + 1}</span>
              <div>
                <h3>{stage.label}</h3>
                <p>{stage.summary}</p>
              </div>
            </li>
          ))}
        </ol>
      </section>

      <section
        className="panel alpha-guardrail"
        aria-labelledby="guardrail-title"
      >
        <h2 id="guardrail-title">ALPHA operating mode</h2>
        <p>
          Decisions only update local SQLite-backed state. Choosing “Recommend
          Unsubscribe Later” records intent for later review and never calls
          Gmail or an external unsubscribe flow.
        </p>
      </section>

      {errorMessage ? (
        <section className="panel error-panel" role="alert">
          <h2>Workflow error</h2>
          <p>{errorMessage}</p>
        </section>
      ) : null}

      <div className="review-layout">
        <section className="panel review-column" aria-labelledby="review-title">
          <div className="section-header">
            <div>
              <p className="eyebrow">Review surface</p>
              <h2 id="review-title">Review candidates</h2>
            </div>
            <p className="queue-copy">
              Suggestions are bounded heuristics only. A candidate does not
              leave review until you choose an explicit decision.
            </p>
          </div>

          {isLoading ? (
            <p className="status-copy" role="status">
              Loading the local candidate queue...
            </p>
          ) : candidates.length === 0 ? (
            <div className="empty-state">
              <h3>No review items remain.</h3>
              <p>
                All current demo candidates are processed. Refresh to confirm
                that no new local items were added.
              </p>
            </div>
          ) : (
            <ul className="candidate-list">
              {candidates.map((candidate) => (
                <li className="candidate-card" key={candidate.id}>
                  <div className="candidate-header">
                    <div>
                      <p className="candidate-source">
                        {candidate.sender_name}
                      </p>
                      <h3>{candidate.subject}</h3>
                      <p className="candidate-email">
                        {candidate.sender_email}
                      </p>
                    </div>
                    <span className="state-pill">
                      {processingStateLabels[candidate.processing_state]}
                    </span>
                  </div>

                  <dl className="candidate-meta">
                    <div>
                      <dt>Mailbox</dt>
                      <dd>{candidate.mailbox_category}</dd>
                    </div>
                    <div>
                      <dt>Signal</dt>
                      <dd>{signalLabels[candidate.classifier_signal]}</dd>
                    </div>
                    <div>
                      <dt>Suggested</dt>
                      <dd>
                        {decisionActionLabels[candidate.suggested_decision]}
                      </dd>
                    </div>
                    <div>
                      <dt>Confidence</dt>
                      <dd>{formatConfidence(candidate.confidence)}</dd>
                    </div>
                  </dl>

                  <p className="candidate-reason">
                    {candidate.candidate_reason}
                  </p>

                  <div
                    className="candidate-actions"
                    aria-label={`Decide how to handle ${candidate.sender_name}`}
                  >
                    {(
                      Object.entries(decisionActionLabels) as [
                        DecisionValue,
                        string,
                      ][]
                    ).map(([decision, label]) => (
                      <button
                        className="decision-button"
                        key={decision}
                        type="button"
                        disabled={submittingCandidateId === candidate.id}
                        onClick={() => {
                          void handleDecision(candidate.id, decision);
                        }}
                      >
                        {submittingCandidateId === candidate.id
                          ? "Saving decision..."
                          : label}
                      </button>
                    ))}
                  </div>

                  <p className="candidate-footnote">
                    No external email action is executed here. This decision
                    only changes local ALPHA state.
                  </p>
                </li>
              ))}
            </ul>
          )}
        </section>

        <aside className="panel history-column" aria-labelledby="history-title">
          <div className="section-header compact-header">
            <div>
              <p className="eyebrow">Recorded outcomes</p>
              <h2 id="history-title">Previous decisions</h2>
            </div>
          </div>

          {isLoading ? (
            <p className="status-copy">Loading decision history...</p>
          ) : decisions.length === 0 ? (
            <div className="empty-state compact-empty-state">
              <h3>No decisions recorded yet.</h3>
              <p>
                The history panel will update after the first explicit choice.
              </p>
            </div>
          ) : (
            <ul className="history-list">
              {decisions.map((decision) => (
                <li className="history-item" key={decision.id}>
                  <p className="history-label">
                    {decisionHistoryLabels[decision.decision]}
                  </p>
                  <strong>{decision.candidate.sender_name}</strong>
                  <p>{decision.candidate.subject}</p>
                  <p>{formatDecisionTimestamp(decision.created_at)}</p>
                  <p>External action: not executed</p>
                  {decision.note ? <p>{decision.note}</p> : null}
                </li>
              ))}
            </ul>
          )}
        </aside>
      </div>
    </section>
  );
}
