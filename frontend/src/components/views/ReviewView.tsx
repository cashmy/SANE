import { Fragment, useEffect, useState } from "react";

import {
  createBatchDecision,
  createDecision,
  listEmailAccounts,
  listDecisions,
  listIngestionRuns,
  listSources,
} from "../../services/api";
import type { EmailAccountInfo, IngestionRunSummary } from "../../types/auth";
import {
  decisionActionLabels,
  processingStateLabels,
  signalLabels,
  type CandidateSignal,
  type DecisionRecord,
  type DecisionValue,
  type PaginationMeta,
  type SourceRow,
} from "../../types/workflow";

const toErrorMessage = (error: unknown) => {
  if (error instanceof Error) return error.message;
  return "The source review queue could not be loaded.";
};

const defaultPagination: PaginationMeta = {
  page: 1,
  page_size: 5,
  total_items: 0,
  total_pages: 1,
  has_previous: false,
  has_next: false,
};

const PAGE_SIZE_OPTIONS = [5, 10, 20];

const pluralize = (count: number, singular: string, plural = `${singular}s`) =>
  count === 1 ? singular : plural;

const formatTimestamp = (value: string | null) => {
  if (!value) return "No timestamp recorded";

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "No timestamp recorded";

  return new Intl.DateTimeFormat("en", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
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

const getSenderDomainFallback = (senderEmails: string[]) => {
  for (const senderEmail of senderEmails) {
    const domain = senderEmail.split("@")[1]?.trim().toLowerCase();
    if (domain) return domain;
  }
  return null;
};

interface ReviewViewProps {
  isLocalAlpha: boolean;
  onOpenConnections: () => void;
}

export function ReviewView({
  isLocalAlpha,
  onOpenConnections,
}: ReviewViewProps) {
  const [sources, setSources] = useState<SourceRow[]>([]);
  const [accounts, setAccounts] = useState<EmailAccountInfo[]>([]);
  const [runsByAccount, setRunsByAccount] = useState<
    Record<number, IngestionRunSummary[]>
  >({});
  const [connectedAccountCount, setConnectedAccountCount] = useState(0);
  const [availableCategories, setAvailableCategories] = useState<string[]>([]);
  const [decisionHistoryCount, setDecisionHistoryCount] = useState(0);
  const [pagination, setPagination] =
    useState<PaginationMeta>(defaultPagination);
  const [isLoading, setIsLoading] = useState(true);
  const [accountsLoaded, setAccountsLoaded] = useState(isLocalAlpha);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [submittingKey, setSubmittingKey] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [signalFilter, setSignalFilter] = useState<"" | CandidateSignal>("");
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(5);
  const [refreshNonce, setRefreshNonce] = useState(0);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [selectedAccountId, setSelectedAccountId] = useState<number | null>(
    null,
  );
  const [expandedSourceId, setExpandedSourceId] = useState<number | null>(null);

  useEffect(() => {
    let cancelled = false;

    if (isLocalAlpha) {
      return () => {
        cancelled = true;
      };
    }

    if (isLocalAlpha) {
      setAccounts([]);
      setRunsByAccount({});
      setConnectedAccountCount(0);
      setSelectedAccountId(null);
      setAccountsLoaded(true);
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

    const loadData = async () => {
      setIsLoading(true);
      setErrorMessage(null);
      try {
        const [sourceResponse, decisionResponse] = await Promise.all([
          listSources({
            page,
            pageSize,
            search,
            category: categoryFilter || undefined,
            signal: signalFilter || undefined,
            emailAccountId: selectedAccountId ?? undefined,
          }),
          listDecisions({
            page: 1,
            pageSize: 1,
            emailAccountId: selectedAccountId ?? undefined,
          }),
        ]);

        if (cancelled) return;

        setSources(sourceResponse.items);
        setAvailableCategories(sourceResponse.available_categories);
        setPagination(sourceResponse.pagination);
        setDecisionHistoryCount(decisionResponse.pagination.total_items);
        setSelectedIds((current) =>
          current.filter((id) =>
            sourceResponse.items.some((source) => source.id === id),
          ),
        );
        setExpandedSourceId((current) =>
          current !== null &&
          sourceResponse.items.some((source) => source.id === current)
            ? current
            : null,
        );

        if (sourceResponse.pagination.page !== page) {
          setPage(sourceResponse.pagination.page);
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

    void loadData();

    return () => {
      cancelled = true;
    };
  }, [
    accountsLoaded,
    categoryFilter,
    isLocalAlpha,
    page,
    pageSize,
    refreshNonce,
    search,
    selectedAccountId,
    signalFilter,
  ]);

  const requestRefresh = (affectedCount: number) => {
    setSelectedIds([]);
    setExpandedSourceId(null);
    if (sources.length <= affectedCount && pagination.page > 1) {
      setPage(pagination.page - 1);
      return;
    }
    setRefreshNonce((value) => value + 1);
  };

  const handleDecision = async (sourceId: number, decision: DecisionValue) => {
    setSubmittingKey(`source-${sourceId}`);
    setErrorMessage(null);
    setStatusMessage(null);
    try {
      await createDecision({
        source_id: sourceId,
        decision,
        confirmed: true,
      });
      requestRefresh(1);
    } catch (error) {
      setErrorMessage(toErrorMessage(error));
    } finally {
      setSubmittingKey(null);
    }
  };

  const handleBatchDecision = async (decision: DecisionValue) => {
    if (selectedIds.length === 0) return;

    const label = decisionActionLabels[decision];
    const confirmed = window.confirm(
      `Apply "${label}" to ${selectedIds.length} selected ${pluralize(selectedIds.length, "source")}? This updates local SANE state only.`,
    );

    if (!confirmed) return;

    setSubmittingKey("batch");
    setErrorMessage(null);
    setStatusMessage(null);

    try {
      const result = await createBatchDecision({
        source_ids: selectedIds,
        decision,
        confirmed: true,
      });

      setStatusMessage(
        `${result.applied.length} ${pluralize(result.applied.length, "source")} updated${
          result.unchanged.length
            ? `, ${result.unchanged.length} unchanged`
            : ""
        }.`,
      );
      requestRefresh(result.applied.length);
    } catch (error) {
      setErrorMessage(toErrorMessage(error));
    } finally {
      setSubmittingKey(null);
    }
  };

  const toggleSelection = (sourceId: number, checked: boolean) => {
    setSelectedIds((current) => {
      if (checked) {
        return current.includes(sourceId) ? current : [...current, sourceId];
      }
      return current.filter((id) => id !== sourceId);
    });
  };

  const toggleSelectAllOnPage = (checked: boolean) => {
    const visibleIds = sources.map((source) => source.id);
    setSelectedIds((current) => {
      if (checked) {
        return [...new Set([...current, ...visibleIds])];
      }
      return current.filter((id) => !visibleIds.includes(id));
    });
  };

  const allOnPageSelected =
    sources.length > 0 &&
    sources.every((source) => selectedIds.includes(source.id));
  const selectedAccount =
    selectedAccountId === null
      ? null
      : (accounts.find((account) => account.id === selectedAccountId) ?? null);
  const latestSelectedRun =
    selectedAccount === null
      ? null
      : ((runsByAccount[selectedAccount.id] ?? [])[0] ?? null);
  const allRuns = Object.values(runsByAccount).flat();
  const hasCompletedRunWithSources = allRuns.some(
    (run) => run.status === "completed" && run.source_count_seen > 0,
  );
  const hasCompletedRunWithoutSources = allRuns.some(
    (run) => run.status === "completed" && run.source_count_seen === 0,
  );
  const filtersActive = Boolean(
    search.trim() || categoryFilter || signalFilter,
  );
  const guidedEmptyState =
    !isLocalAlpha &&
    !filtersActive &&
    !errorMessage &&
    !isLoading &&
    sources.length === 0 &&
    pagination.total_items === 0 &&
    decisionHistoryCount === 0
      ? connectedAccountCount === 0
        ? {
            title: "Connect Gmail to build your review queue",
            body: "You are signed in, but no Gmail account is connected to this SANE user yet. Go to Connections to connect Gmail before your first bounded scan.",
          }
        : allRuns.length === 0
          ? {
              title: "Run a bounded scan to populate Review",
              body: "Gmail is connected, but no manual scan has run yet. Use Connections to run a bounded scan and then return here to review sources.",
            }
          : hasCompletedRunWithoutSources && !hasCompletedRunWithSources
            ? {
                title: "Last scan completed with no review sources",
                body: "The last bounded scan completed without creating review sources. Check Connections to rerun a manual scan or confirm the mailbox scope.",
              }
            : {
                title: "No sources are ready in Review yet",
                body: "Check Connections for the last run status or start another bounded manual scan before returning to Review.",
              }
      : null;

  const batchDisabled =
    selectedIds.length === 0 || isLoading || submittingKey !== null;

  return (
    <div className="review-view">
      <dl className="summary-strip" aria-label="Review summary">
        <div className="summary-kpi summary-kpi--pending">
          <dt>Pending review</dt>
          <dd>{pagination.total_items}</dd>
          <span className="summary-note">{sources.length} on this page</span>
        </div>
        <div className="summary-kpi summary-kpi--decision">
          <dt>Decision history</dt>
          <dd>{decisionHistoryCount}</dd>
          <span className="summary-note">
            {isLocalAlpha
              ? "Append-only local ALPHA history"
              : "Append-only local events for this mailbox"}
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
          aria-label="Review mailbox scope"
        >
          <div className="mailbox-scope-card__header">
            <div className="mailbox-scope-card__copy">
              <span className="chip chip--neutral">Mailbox scope</span>
              <h2>{selectedAccount?.account_email ?? "Select a mailbox"}</h2>
              <p>
                Review stays scoped to one Gmail account at a time. SANE shows
                stored metadata only and never executes Gmail actions.
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
                aria-label="Review mailbox scope"
                value={selectedAccountId ?? ""}
                onChange={(event) => {
                  setSelectedAccountId(Number(event.target.value));
                  setPage(1);
                  setSelectedIds([]);
                  setExpandedSourceId(null);
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
                {latestSelectedRun.message_count_scanned} messages checked,{" "}
                {latestSelectedRun.source_count_seen} sources seen
              </span>
            ) : null}
          </div>
        </section>
      )}

      {guidedEmptyState ? (
        <section
          className="placeholder-card guided-empty-state"
          aria-label="Review empty state"
        >
          <span className="chip chip--neutral">Manual scan only</span>
          <h2>{guidedEmptyState.title}</h2>
          <p>{guidedEmptyState.body}</p>
          <div className="guided-empty-state__actions">
            <button
              className="btn-secondary"
              type="button"
              onClick={onOpenConnections}
            >
              Go to Connections
            </button>
          </div>
        </section>
      ) : (
        <>
          <div className="filter-bar">
            <div className="filter-search">
              <input
                className="search-input"
                type="search"
                placeholder="Search sources…"
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value);
                  setPage(1);
                }}
                aria-label="Search sources"
              />
            </div>
            <div className="filter-controls">
              <select
                className="filter-select"
                value={categoryFilter}
                onChange={(e) => {
                  setCategoryFilter(e.target.value);
                  setPage(1);
                }}
                aria-label="Filter by category"
              >
                <option value="">All categories</option>
                {availableCategories.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat}
                  </option>
                ))}
              </select>
              <select
                className="filter-select"
                value={signalFilter}
                onChange={(e) => {
                  setSignalFilter(e.target.value as "" | CandidateSignal);
                  setPage(1);
                }}
                aria-label="Filter by signal"
              >
                <option value="">All signals</option>
                {(Object.keys(signalLabels) as CandidateSignal[]).map((sig) => (
                  <option key={sig} value={sig}>
                    {signalLabels[sig]}
                  </option>
                ))}
              </select>
              <button
                className="btn-secondary"
                type="button"
                onClick={() => {
                  setRefreshNonce((value) => value + 1);
                }}
                disabled={isLoading || submittingKey !== null}
              >
                Refresh
              </button>
            </div>
          </div>

          <div
            className={`batch-bar${selectedIds.length > 0 ? " batch-bar--active" : ""}`}
            aria-label="Batch decision controls"
          >
            <div className="batch-context">
              <span
                className={`selection-badge${selectedIds.length > 0 ? " selection-badge--active" : ""}`}
              >
                {selectedIds.length}
              </span>
              <div className="batch-summary">
                <strong>
                  {selectedIds.length > 0
                    ? `${selectedIds.length} ${pluralize(selectedIds.length, "source")} selected`
                    : "Batch actions"}
                </strong>
                <span>
                  {sources.length} shown · Page {pagination.page}/
                  {pagination.total_pages} · {pagination.total_items} pending
                </span>
              </div>
            </div>
            <div className="batch-actions">
              {(
                Object.entries(decisionActionLabels) as [
                  DecisionValue,
                  string,
                ][]
              ).map(([decision, label]) => (
                <button
                  key={decision}
                  className={`btn-action btn-action--${decision.replace(/_/g, "-")}`}
                  type="button"
                  onClick={() => {
                    void handleBatchDecision(decision);
                  }}
                  disabled={batchDisabled}
                >
                  {submittingKey === "batch" ? "Applying…" : `Apply ${label}`}
                </button>
              ))}
            </div>
          </div>

          {isLoading ? (
            <p className="status-msg" role="status">
              Loading sources…
            </p>
          ) : (
            <>
              <div className="table-container">
                <table
                  className="source-table"
                  aria-label="Source review queue"
                >
                  <thead>
                    <tr>
                      <th className="select-cell">
                        <input
                          className="row-checkbox"
                          type="checkbox"
                          aria-label="Select all sources on this page"
                          checked={allOnPageSelected}
                          onChange={(e) => {
                            toggleSelectAllOnPage(e.target.checked);
                          }}
                        />
                      </th>
                      <th>Source</th>
                      <th>Sender emails</th>
                      <th>Email count</th>
                      <th>Category</th>
                      <th>Signal</th>
                      <th>Suggested</th>
                      <th>State</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {sources.length === 0 ? (
                      <tr>
                        <td colSpan={9} className="empty-row">
                          {pagination.total_items === 0
                            ? "No pending sources remain."
                            : "No sources match the current server-side filters."}
                        </td>
                      </tr>
                    ) : (
                      sources.map((source) => {
                        const isExpanded = expandedSourceId === source.id;
                        const senderDomain =
                          source.sender_domain ??
                          getSenderDomainFallback(source.sender_emails);
                        const representativeLabels =
                          source.representative_label_ids?.join(", ") ?? null;

                        return (
                          <Fragment key={source.id}>
                            <tr
                              className={`source-row${selectedIds.includes(source.id) ? " source-row--selected" : ""}`}
                            >
                              <td className="select-cell">
                                <input
                                  className="row-checkbox"
                                  type="checkbox"
                                  checked={selectedIds.includes(source.id)}
                                  aria-label={`Select ${source.source_name}`}
                                  onChange={(e) => {
                                    toggleSelection(
                                      source.id,
                                      e.target.checked,
                                    );
                                  }}
                                />
                              </td>
                              <td className="col-source">
                                <span className="source-name">
                                  {source.source_name}
                                </span>
                                <span className="source-subject">
                                  {source.representative_subject}
                                </span>
                                <button
                                  className="evidence-toggle"
                                  type="button"
                                  aria-expanded={isExpanded}
                                  aria-controls={`review-evidence-${source.id}`}
                                  onClick={() => {
                                    setExpandedSourceId((current) =>
                                      current === source.id ? null : source.id,
                                    );
                                  }}
                                >
                                  {isExpanded
                                    ? "Hide evidence"
                                    : "Show evidence"}
                                </button>
                              </td>
                              <td>
                                <div className="sender-list">
                                  {source.sender_emails.map((senderEmail) => (
                                    <span key={senderEmail}>{senderEmail}</span>
                                  ))}
                                </div>
                              </td>
                              <td className="col-count">
                                <div className="count-metric">
                                  <strong>{source.email_count}</strong>
                                  <span>emails</span>
                                </div>
                              </td>
                              <td>{source.mailbox_category}</td>
                              <td>
                                <span
                                  className={`chip chip--signal chip--${source.classifier_signal.replace(/_/g, "-")}`}
                                >
                                  {signalLabels[source.classifier_signal]}
                                </span>
                              </td>
                              <td>
                                <span
                                  className={`chip chip--decision chip--${source.suggested_decision.replace(/_/g, "-")}`}
                                >
                                  {
                                    decisionActionLabels[
                                      source.suggested_decision
                                    ]
                                  }
                                </span>
                              </td>
                              <td>
                                <span
                                  className={`chip chip--state chip--${source.processing_state.replace(/_/g, "-")}`}
                                >
                                  {
                                    processingStateLabels[
                                      source.processing_state
                                    ]
                                  }
                                </span>
                              </td>
                              <td className="col-actions">
                                <div className="row-actions">
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
                                        submittingKey === `source-${source.id}`
                                      }
                                      onClick={() => {
                                        void handleDecision(
                                          source.id,
                                          decision,
                                        );
                                      }}
                                    >
                                      {submittingKey === `source-${source.id}`
                                        ? "…"
                                        : label}
                                    </button>
                                  ))}
                                </div>
                              </td>
                            </tr>
                            {isExpanded ? (
                              <tr className="source-evidence-row">
                                <td
                                  colSpan={9}
                                  id={`review-evidence-${source.id}`}
                                >
                                  <div className="source-evidence">
                                    <div className="source-evidence__item">
                                      <strong>Mailbox scope</strong>
                                      <span>
                                        {selectedAccount?.account_email ??
                                          "Local ALPHA review queue"}
                                      </span>
                                    </div>
                                    <div className="source-evidence__item">
                                      <strong>Sender domain</strong>
                                      <span>
                                        {senderDomain ??
                                          "No sender domain recorded"}
                                      </span>
                                    </div>
                                    <div className="source-evidence__item">
                                      <strong>Representative subject</strong>
                                      <span>
                                        {source.representative_subject}
                                      </span>
                                    </div>
                                    {source.representative_message_timestamp ? (
                                      <div className="source-evidence__item">
                                        <strong>
                                          Representative message date
                                        </strong>
                                        <span>
                                          {formatTimestamp(
                                            source.representative_message_timestamp,
                                          )}
                                        </span>
                                      </div>
                                    ) : null}
                                    {source.representative_message_id ? (
                                      <div className="source-evidence__item">
                                        <strong>
                                          Representative message id
                                        </strong>
                                        <span>
                                          {source.representative_message_id}
                                        </span>
                                      </div>
                                    ) : null}
                                    {representativeLabels ? (
                                      <div className="source-evidence__item">
                                        <strong>Representative labels</strong>
                                        <span>{representativeLabels}</span>
                                      </div>
                                    ) : null}
                                    {source.representative_list_id ? (
                                      <div className="source-evidence__item">
                                        <strong>List-ID</strong>
                                        <span>
                                          {source.representative_list_id}
                                        </span>
                                      </div>
                                    ) : null}
                                    {source.has_list_unsubscribe ? (
                                      <div className="source-evidence__item">
                                        <strong>List-Unsubscribe header</strong>
                                        <span>Present</span>
                                      </div>
                                    ) : null}
                                    <div className="source-evidence__item">
                                      <strong>Classifier reason</strong>
                                      <span>{source.candidate_reason}</span>
                                    </div>
                                    <div className="source-evidence__item">
                                      <strong>Current local decision</strong>
                                      <span>
                                        {source.current_decision
                                          ? decisionActionLabels[
                                              source.current_decision
                                            ]
                                          : "No local decision recorded"}
                                      </span>
                                    </div>
                                    <div className="source-evidence__item">
                                      <strong>Latest scan context</strong>
                                      <span>
                                        {latestSelectedRun
                                          ? `${latestSelectedRun.message_count_scanned} messages checked on ${formatTimestamp(
                                              latestSelectedRun.completed_at ??
                                                latestSelectedRun.started_at,
                                            )}`
                                          : "No scan recorded for this mailbox yet"}
                                      </span>
                                    </div>
                                  </div>
                                </td>
                              </tr>
                            ) : null}
                          </Fragment>
                        );
                      })
                    )}
                  </tbody>
                </table>
              </div>

              <div className="pagination-bar">
                <div className="pagination-cluster">
                  <span className="pagination-pill">
                    Page {pagination.page} of {pagination.total_pages}
                  </span>
                  <span className="pagination-summary">
                    {pagination.total_items} queued{" "}
                    {pluralize(pagination.total_items, "source")}
                  </span>
                </div>
                <div className="pagination-controls">
                  <label className="page-size-control">
                    Page size
                    <select
                      className="filter-select page-size-select"
                      aria-label="Page size"
                      value={pageSize}
                      onChange={(e) => {
                        setPageSize(Number(e.target.value));
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
                      submittingKey !== null
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
                      submittingKey !== null
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
        </>
      )}
      <p className="table-footnote">
        No external email actions are executed in this ALPHA. Single and batch
        decisions update local SANE state only.
      </p>
    </div>
  );
}
