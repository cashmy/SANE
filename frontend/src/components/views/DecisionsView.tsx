import { useEffect, useState } from "react";

import {
  createDecision,
  listDecisions,
  listEmailAccounts,
  listIngestionRuns,
} from "../../services/api";
import type { IngestionRunSummary } from "../../types/auth";
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

interface DecisionsViewProps {
  isLocalAlpha: boolean;
  onOpenConnections: () => void;
  onOpenReview: () => void;
}

export function DecisionsView({
  isLocalAlpha,
  onOpenConnections,
  onOpenReview,
}: DecisionsViewProps) {
  const [decisions, setDecisions] = useState<DecisionRecord[]>([]);
  const [runsByAccount, setRunsByAccount] = useState<
    Record<number, IngestionRunSummary[]>
  >({});
  const [connectedAccountCount, setConnectedAccountCount] = useState(0);
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
        const [response, accounts] = await Promise.all([
          listDecisions(),
          listEmailAccounts(),
        ]);
        const runEntries = await Promise.all(
          accounts.map(async (account) => {
            const runs = await listIngestionRuns(account.id);
            return [account.id, runs] as const;
          }),
        );
        if (cancelled) return;
        setDecisions(response.items);
        setRunsByAccount(Object.fromEntries(runEntries));
        setConnectedAccountCount(
          accounts.filter(
            (account) => account.connection_status === "connected",
          ).length,
        );
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

  const currentCount = decisions.filter(
    (decision) => decision.is_current,
  ).length;
  const revisionCount = decisions.filter(
    (decision) => decision.is_revision,
  ).length;
  const allRuns = Object.values(runsByAccount).flat();
  const hasCompletedRunWithSources = allRuns.some(
    (run) => run.status === "completed" && run.source_count_created > 0,
  );
  const hasCompletedRunWithoutSources = allRuns.some(
    (run) => run.status === "completed" && run.source_count_created === 0,
  );
  const emptyState =
    !errorMessage && !isLoading && decisions.length === 0
      ? isLocalAlpha
        ? {
            title: "No local decisions recorded yet",
            body: "Use Review to record your first local decision against the demo sources.",
            actionLabel: "Go to Review",
            action: onOpenReview,
          }
        : connectedAccountCount === 0
          ? {
              title: "No decisions recorded yet",
              body: "Connect Gmail in Connections, then run a bounded manual scan before you start reviewing sources.",
              actionLabel: "Go to Connections",
              action: onOpenConnections,
            }
          : allRuns.length === 0
            ? {
                title: "Run a scan before decisions begin",
                body: "Gmail is connected, but no bounded scan has run yet. Use Connections to start the first manual scan.",
                actionLabel: "Go to Connections",
                action: onOpenConnections,
              }
            : hasCompletedRunWithoutSources && !hasCompletedRunWithSources
              ? {
                  title:
                    "No decisions yet because no review sources were created",
                  body: "The last bounded scan completed without creating review sources. Check Connections before the next scan.",
                  actionLabel: "Go to Connections",
                  action: onOpenConnections,
                }
              : {
                  title: "No decisions recorded yet",
                  body: "Review sources after your next bounded scan to start recording local decisions.",
                  actionLabel: "Go to Review",
                  action: onOpenReview,
                }
      : null;

  return (
    <div className="decisions-view">
      <dl className="summary-strip" aria-label="Decision summary">
        <div className="summary-kpi summary-kpi--decision">
          <dt>Current source states</dt>
          <dd>{currentCount}</dd>
          <span className="summary-note">Latest local decisions</span>
        </div>
        <div className="summary-kpi summary-kpi--revision">
          <dt>Revision events</dt>
          <dd>{revisionCount}</dd>
          <span className="summary-note">Append-only history</span>
        </div>
        <div className="summary-kpi summary-kpi--safety">
          <dt>External actions</dt>
          <dd>
            <span className="chip chip--neutral">Not executed</span>
          </dd>
          <span className="summary-note">Local-only ALPHA</span>
        </div>
      </dl>

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
      ) : emptyState ? (
        <section
          className="placeholder-card guided-empty-state"
          aria-label="Decision history empty state"
        >
          <span className="chip chip--neutral">Local-only ALPHA</span>
          <h2>{emptyState.title}</h2>
          <p>{emptyState.body}</p>
          <div className="guided-empty-state__actions">
            <button
              className="btn-secondary"
              type="button"
              onClick={emptyState.action}
            >
              {emptyState.actionLabel}
            </button>
          </div>
        </section>
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
              {decisions.map((d) => (
                <tr
                  key={d.id}
                  className={`source-row decision-row${d.is_current ? " decision-row--current" : " decision-row--historic"}`}
                >
                  <td className="col-source">
                    <span className="source-name">{d.source.source_name}</span>
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
                        className={`chip ${d.is_current ? "chip--current" : "chip--superseded"}`}
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
                  <td className="col-time">{formatTimestamp(d.created_at)}</td>
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
              ))}
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
