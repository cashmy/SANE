import { useEffect, useState } from "react";

import { createDecision, listDecisions } from "../../services/api";
import {
  decisionActionLabels,
  decisionHistoryLabels,
  type DecisionRecord,
  type DecisionValue,
} from "../../types/workflow";

const formatTimestamp = (value: string) => {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "—";
  return new Intl.DateTimeFormat("en", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
};

const toErrorMessage = (error: unknown) => {
  if (error instanceof Error) return error.message;
  return "Decision history could not be loaded.";
};

export function DecisionsView() {
  const [decisions, setDecisions] = useState<DecisionRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [submittingSourceId, setSubmittingSourceId] = useState<number | null>(
    null,
  );

  const loadDecisions = async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const response = await listDecisions();
      setDecisions(response.items);
    } catch (error) {
      setErrorMessage(toErrorMessage(error));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      setIsLoading(true);
      setErrorMessage(null);
      try {
        const response = await listDecisions();
        if (cancelled) return;
        setDecisions(response.items);
      } catch (error) {
        if (!cancelled) {
          setErrorMessage(toErrorMessage(error));
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    };

    void load();

    return () => {
      cancelled = true;
    };
  }, []);

  const handleRevision = async (sourceId: number, decision: DecisionValue) => {
    setSubmittingSourceId(sourceId);
    setErrorMessage(null);
    setStatusMessage(null);
    try {
      const updated = await createDecision({
        source_id: sourceId,
        decision,
        confirmed: true,
      });
      setStatusMessage(
        `${updated.source.source_name} updated to ${decisionActionLabels[updated.decision]}.`,
      );
      await loadDecisions();
    } catch (error) {
      setErrorMessage(toErrorMessage(error));
    } finally {
      setSubmittingSourceId(null);
    }
  };

  return (
    <div className="decisions-view">
      {errorMessage && (
        <div className="alert-error" role="alert">
          {errorMessage}
        </div>
      )}
      {statusMessage && (
        <p className="status-msg" role="status">
          {statusMessage}
        </p>
      )}
      {isLoading ? (
        <p className="status-msg" role="status">
          Loading decision history…
        </p>
      ) : (
        <div className="table-container">
          <table className="source-table" aria-label="Source decision history">
            <thead>
              <tr>
                <th>Source</th>
                <th>Representative message</th>
                <th>Decision</th>
                <th>History</th>
                <th>External action</th>
                <th>Recorded</th>
                <th>Change decision</th>
              </tr>
            </thead>
            <tbody>
              {decisions.length === 0 ? (
                <tr>
                  <td colSpan={7} className="empty-row">
                    No decisions recorded yet.
                  </td>
                </tr>
              ) : (
                decisions.map((d) => (
                  <tr key={d.id} className="source-row">
                    <td className="col-source">
                      <span className="source-name">
                        {d.source.source_name}
                      </span>
                      <span className="source-email">
                        {d.source.sender_emails.join(", ")}
                      </span>
                    </td>
                    <td>
                      <span className="source-subject">
                        {d.source.representative_subject}
                      </span>
                      <span className="source-reason">
                        {d.source.mailbox_category}
                      </span>
                    </td>
                    <td>
                      <span
                        className={`chip chip--decision chip--${d.decision.replace(/_/g, "-")}`}
                      >
                        {decisionHistoryLabels[d.decision]}
                      </span>
                    </td>
                    <td>
                      <div className="history-flags">
                        <span
                          className={`chip ${d.is_current ? "chip--current" : "chip--neutral"}`}
                        >
                          {d.is_current ? "Current" : "Superseded"}
                        </span>
                        {d.is_revision && (
                          <span className="chip chip--revision">Revision</span>
                        )}
                      </div>
                    </td>
                    <td>
                      <span className="chip chip--neutral">Not executed</span>
                    </td>
                    <td className="col-time">
                      {formatTimestamp(d.created_at)}
                    </td>
                    <td className="col-actions">
                      {d.is_current ? (
                        <div className="row-actions row-actions--inline">
                          {(
                            Object.entries(decisionActionLabels) as [
                              DecisionValue,
                              string,
                            ][]
                          ).map(([decision, label]) => (
                            <button
                              className={`btn-action btn-action--${decision.replace(/_/g, "-")}`}
                              key={decision}
                              type="button"
                              disabled={
                                submittingSourceId === d.source.id ||
                                decision === d.decision
                              }
                              onClick={() => {
                                void handleRevision(d.source.id, decision);
                              }}
                            >
                              {submittingSourceId === d.source.id ? "…" : label}
                            </button>
                          ))}
                        </div>
                      ) : (
                        <span className="source-reason">Revision recorded</span>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}
      <p className="table-footnote">
        Revision history remains append-only in ALPHA. Changing a current source
        decision records a new local event and never executes an external email
        action.
      </p>
    </div>
  );
}
