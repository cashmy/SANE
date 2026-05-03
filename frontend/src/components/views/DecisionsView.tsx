import { useEffect, useState } from "react";

import {
  createDecision,
  listDecisions,
  listEmailAccounts,
  listIngestionRuns,
} from "../../services/api";
import type { EmailAccountInfo, IngestionRunSummary } from "../../types/auth";
import {
  decisionActionLabels,
  decisionHistoryLabels,
  type DecisionRecord,
  type DecisionValue,
  type PaginationMeta,
} from "../../types/workflow";

const defaultPagination: PaginationMeta = {
  page: 1,
  page_size: 5,
  total_items: 0,
  total_pages: 1,
  has_previous: false,
  has_next: false,
};

const PAGE_SIZE_OPTIONS = [5, 10, 20];

const formatTimestamp = (value: string | null) => {
  if (!value) return "—";
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

const mailboxStatusLabel = (status: EmailAccountInfo["connection_status"]) => {
  if (status === "connected") return "Connected";
  if (status === "disconnected") return "Disconnected";
  if (status === "expired") return "Expired";
  if (status === "revoked") return "Revoked";
  if (status === "error") return "Error";
  return "Local only";
};

const mailboxStatusChipClass = (
  status: EmailAccountInfo["connection_status"],
) => {
  if (status === "connected") return "chip chip--connected";
  if (status === "disconnected") return "chip chip--disconnected";
  if (status === "expired") return "chip chip--warning";
  if (status === "revoked" || status === "error") return "chip chip--danger";
  return "chip chip--neutral";
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
  const [accounts, setAccounts] = useState<EmailAccountInfo[]>([]);
  const [runsByAccount, setRunsByAccount] = useState<
    Record<number, IngestionRunSummary[]>
  >({});
  const [connectedAccountCount, setConnectedAccountCount] = useState(0);
  const [pagination, setPagination] =
    useState<PaginationMeta>(defaultPagination);
  const [isLoading, setIsLoading] = useState(true);
  const [accountsLoaded, setAccountsLoaded] = useState(isLocalAlpha);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [submittingSourceId, setSubmittingSourceId] = useState<number | null>(
    null,
  );
  const [selectedAccountId, setSelectedAccountId] = useState<number | null>(
    null,
  );
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(5);
  const [refreshNonce, setRefreshNonce] = useState(0);

  useEffect(() => {
    let cancelled = false;

    if (isLocalAlpha) {
      return () => {
        cancelled = true;
      };
    }

    const loadAccountContext = async () => {
      setErrorMessage(null);
      try {
        const nextAccounts = await listEmailAccounts();
        const runEntries = await Promise.all(
          nextAccounts.map(async (account) => {
            const runs = await listIngestionRuns(account.id);
            return [account.id, runs] as const;
          }),
        );
        if (cancelled) return;
        setAccounts(nextAccounts);
        setRunsByAccount(Object.fromEntries(runEntries));
        setConnectedAccountCount(
          nextAccounts.filter(
            (account) => account.connection_status === "connected",
          ).length,
        );
        setSelectedAccountId((current) => {
          if (
            current !== null &&
            nextAccounts.some((account) => account.id === current)
          ) {
            return current;
          }
          return nextAccounts[0]?.id ?? null;
        });
      } catch (error) {
        if (!cancelled) {
          setErrorMessage(toErrorMessage(error));
        }
      } finally {
        if (!cancelled) {
          setAccountsLoaded(true);
        }
      }
    };

    void loadAccountContext();

    return () => {
      cancelled = true;
    };
  }, [isLocalAlpha]);

  useEffect(() => {
    let cancelled = false;

    if (!accountsLoaded) {
      return () => {
        cancelled = true;
      };
    }

    if (!isLocalAlpha && accounts.length > 0 && selectedAccountId === null) {
      return () => {
        cancelled = true;
      };
    }

    const loadDecisions = async () => {
      setIsLoading(true);
      setErrorMessage(null);
      try {
        const response = await listDecisions({
          page,
          pageSize,
          emailAccountId: selectedAccountId ?? undefined,
        });
        if (cancelled) return;
        setDecisions(response.items);
        setPagination(response.pagination);
        if (response.pagination.page !== page) {
          setPage(response.pagination.page);
        }
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

    void loadDecisions();

    return () => {
      cancelled = true;
    };
  }, [
    accountsLoaded,
    isLocalAlpha,
    page,
    pageSize,
    refreshNonce,
    selectedAccountId,
  ]);

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
      setRefreshNonce((value) => value + 1);
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
    (run) => run.status === "completed" && run.source_count_seen > 0,
  );
  const hasCompletedRunWithoutSources = allRuns.some(
    (run) => run.status === "completed" && run.source_count_seen === 0,
  );
  const selectedAccount =
    selectedAccountId === null
      ? null
      : (accounts.find((account) => account.id === selectedAccountId) ?? null);
  const latestSelectedRun =
    selectedAccount === null
      ? null
      : ((runsByAccount[selectedAccount.id] ?? [])[0] ?? null);
  const emptyState =
    !errorMessage && !isLoading && pagination.total_items === 0
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
          <dt>History events</dt>
          <dd>{pagination.total_items}</dd>
          <span className="summary-note">
            {isLocalAlpha
              ? "Append-only local ALPHA decisions"
              : "Append-only local decisions in this mailbox"}
          </span>
        </div>
        <div className="summary-kpi summary-kpi--revision">
          <dt>Rows on this page</dt>
          <dd>{decisions.length}</dd>
          <span className="summary-note">
            {currentCount} current · {revisionCount} revisions
          </span>
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
      {!isLocalAlpha && accounts.length > 0 && (
        <section
          className="mailbox-scope-card"
          aria-label="Decision mailbox scope"
        >
          <div className="mailbox-scope-card__header">
            <div className="mailbox-scope-card__copy">
              <span className="chip chip--neutral">Mailbox scope</span>
              <h2>{selectedAccount?.account_email ?? "Select a mailbox"}</h2>
              <p>
                Decision history stays scoped to one Gmail account at a time.
                Current and superseded rows remain append-only local history.
              </p>
            </div>
            {selectedAccount ? (
              <span
                className={mailboxStatusChipClass(
                  selectedAccount.connection_status,
                )}
              >
                {mailboxStatusLabel(selectedAccount.connection_status)}
              </span>
            ) : null}
          </div>
          <div className="mailbox-scope-card__meta">
            <label className="page-size-control mailbox-scope-card__control">
              Mailbox
              <select
                className="filter-select page-size-select"
                aria-label="Decision mailbox scope"
                value={selectedAccountId ?? ""}
                onChange={(event) => {
                  setSelectedAccountId(Number(event.target.value));
                  setPage(1);
                }}
              >
                {accounts.map((account) => (
                  <option key={account.id} value={account.id}>
                    {account.account_email}
                  </option>
                ))}
              </select>
            </label>
            <span className="pagination-summary">
              {latestSelectedRun
                ? `Latest scan: ${formatTimestamp(
                    latestSelectedRun.completed_at ??
                      latestSelectedRun.started_at,
                  )}`
                : "Latest scan: none recorded"}
            </span>
            {latestSelectedRun ? (
              <span className="pagination-summary">
                {latestSelectedRun.source_count_seen} sources seen in the last
                run
              </span>
            ) : null}
          </div>
        </section>
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
        <>
          <div className="table-container">
            <table
              className="source-table"
              aria-label="Source decision history"
            >
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
                ))}
              </tbody>
            </table>
          </div>

          <div className="pagination-bar">
            <div className="pagination-cluster">
              <span className="pagination-pill">
                Page {pagination.page} of {pagination.total_pages}
              </span>
              <span className="pagination-summary">
                {pagination.total_items} history events
              </span>
            </div>
            <div className="pagination-controls">
              <label className="page-size-control">
                Page size
                <select
                  className="filter-select page-size-select"
                  aria-label="Decision page size"
                  value={pageSize}
                  onChange={(event) => {
                    setPageSize(Number(event.target.value));
                    setPage(1);
                  }}
                >
                  {PAGE_SIZE_OPTIONS.map((option) => (
                    <option key={option} value={option}>
                      {option}
                    </option>
                  ))}
                </select>
              </label>
              <button
                className="btn-secondary"
                type="button"
                disabled={
                  !pagination.has_previous ||
                  isLoading ||
                  submittingSourceId !== null
                }
                onClick={() => {
                  setPage((current) => Math.max(1, current - 1));
                }}
              >
                Previous
              </button>
              <button
                className="btn-secondary"
                type="button"
                disabled={
                  !pagination.has_next ||
                  isLoading ||
                  submittingSourceId !== null
                }
                onClick={() => {
                  setPage((current) => current + 1);
                }}
              >
                Next
              </button>
            </div>
          </div>
        </>
      )}
      <p className="table-footnote">
        Revision history remains append-only in ALPHA. Changing a current source
        decision records a new local event and never executes an external email
        action.
      </p>
    </div>
  );
}
