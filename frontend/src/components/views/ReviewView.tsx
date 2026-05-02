import { useEffect, useState } from "react";

import {
  createBatchDecision,
  createDecision,
  listDecisions,
  listSources,
} from "../../services/api";
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

export function ReviewView() {
  const [sources, setSources] = useState<SourceRow[]>([]);
  const [decisions, setDecisions] = useState<DecisionRecord[]>([]);
  const [availableCategories, setAvailableCategories] = useState<string[]>([]);
  const [pagination, setPagination] =
    useState<PaginationMeta>(defaultPagination);
  const [isLoading, setIsLoading] = useState(true);
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

  useEffect(() => {
    let cancelled = false;

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
          }),
          listDecisions(),
        ]);

        if (cancelled) return;

        setSources(sourceResponse.items);
        setAvailableCategories(sourceResponse.available_categories);
        setPagination(sourceResponse.pagination);
        setDecisions(decisionResponse.items);
        setSelectedIds((current) =>
          current.filter((id) =>
            sourceResponse.items.some((source) => source.id === id),
          ),
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
  }, [page, pageSize, search, categoryFilter, signalFilter, refreshNonce]);

  const requestRefresh = (affectedCount: number) => {
    setSelectedIds([]);
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
  const decidedCount = decisions.filter(
    (decision) => decision.is_current,
  ).length;
  const revisionCount = decisions.filter(
    (decision) => decision.is_revision,
  ).length;

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
          <dt>Sources with decision</dt>
          <dd>{decidedCount}</dd>
          <span className="summary-note">
            {revisionCount} revisions recorded
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
            Object.entries(decisionActionLabels) as [DecisionValue, string][]
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
            <table className="source-table" aria-label="Source review queue">
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
                  sources.map((source) => (
                    <tr
                      key={source.id}
                      className={`source-row${selectedIds.includes(source.id) ? " source-row--selected" : ""}`}
                    >
                      <td className="select-cell">
                        <input
                          className="row-checkbox"
                          type="checkbox"
                          checked={selectedIds.includes(source.id)}
                          aria-label={`Select ${source.source_name}`}
                          onChange={(e) => {
                            toggleSelection(source.id, e.target.checked);
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
                        <span className="source-reason">
                          {source.candidate_reason}
                        </span>
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
                          {decisionActionLabels[source.suggested_decision]}
                        </span>
                      </td>
                      <td>
                        <span
                          className={`chip chip--state chip--${source.processing_state.replace(/_/g, "-")}`}
                        >
                          {processingStateLabels[source.processing_state]}
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
                              disabled={submittingKey === `source-${source.id}`}
                              onClick={() => {
                                void handleDecision(source.id, decision);
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
                  ))
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
                  !pagination.has_next || isLoading || submittingKey !== null
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
        No external email actions are executed in this ALPHA. Single and batch
        decisions update local SANE state only.
      </p>
    </div>
  );
}
