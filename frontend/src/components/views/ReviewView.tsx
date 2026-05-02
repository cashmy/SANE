import { useEffect, useMemo, useState } from "react";

import {
  createDecision,
  listCandidates,
  listDecisions,
} from "../../services/api";
import {
  decisionActionLabels,
  processingStateLabels,
  signalLabels,
  type Candidate,
  type CandidateSignal,
  type DecisionValue,
} from "../../types/workflow";

const toErrorMessage = (error: unknown) => {
  if (error instanceof Error) return error.message;
  return "The candidate queue could not be loaded.";
};

export function ReviewView() {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [decidedCount, setDecidedCount] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [submittingId, setSubmittingId] = useState<number | null>(null);
  const [search, setSearch] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [signalFilter, setSignalFilter] = useState("");

  const loadData = async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const [candResponse, decResponse] = await Promise.all([
        listCandidates(),
        listDecisions(),
      ]);
      setCandidates(candResponse.items);
      setDecidedCount(decResponse.items.length);
    } catch (error) {
      setErrorMessage(toErrorMessage(error));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    void loadData();
  }, []);

  const handleDecision = async (
    candidateId: number,
    decision: DecisionValue,
  ) => {
    setSubmittingId(candidateId);
    setErrorMessage(null);
    try {
      await createDecision({
        candidate_id: candidateId,
        decision,
        confirmed: true,
      });
      setCandidates((current) => current.filter((c) => c.id !== candidateId));
      setDecidedCount((n) => n + 1);
    } catch (error) {
      setErrorMessage(toErrorMessage(error));
    } finally {
      setSubmittingId(null);
    }
  };

  const categories = useMemo(
    () => [...new Set(candidates.map((c) => c.mailbox_category))],
    [candidates],
  );

  const filtered = useMemo(() => {
    const q = search.toLowerCase();
    return candidates.filter((c) => {
      if (
        q &&
        !c.sender_name.toLowerCase().includes(q) &&
        !c.sender_email.toLowerCase().includes(q)
      ) {
        return false;
      }
      if (categoryFilter && c.mailbox_category !== categoryFilter) return false;
      if (signalFilter && c.classifier_signal !== signalFilter) return false;
      return true;
    });
  }, [candidates, search, categoryFilter, signalFilter]);

  return (
    <div className="review-view">
      <dl className="summary-strip" aria-label="Review summary">
        <div className="summary-kpi">
          <dt>Pending review</dt>
          <dd>{candidates.length}</dd>
        </div>
        <div className="summary-kpi">
          <dt>Decided</dt>
          <dd>{decidedCount}</dd>
        </div>
        <div className="summary-kpi">
          <dt>External actions</dt>
          <dd>
            <span className="chip chip--neutral">Not executed</span>
          </dd>
        </div>
      </dl>

      {errorMessage && (
        <div className="alert-error" role="alert">
          {errorMessage}
        </div>
      )}

      <div className="filter-bar">
        <input
          className="search-input"
          type="search"
          placeholder="Search sources…"
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
          }}
          aria-label="Search sources"
        />
        <select
          className="filter-select"
          value={categoryFilter}
          onChange={(e) => {
            setCategoryFilter(e.target.value);
          }}
          aria-label="Filter by category"
        >
          <option value="">All categories</option>
          {categories.map((cat) => (
            <option key={cat} value={cat}>
              {cat}
            </option>
          ))}
        </select>
        <select
          className="filter-select"
          value={signalFilter}
          onChange={(e) => {
            setSignalFilter(e.target.value);
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
            void loadData();
          }}
          disabled={isLoading || submittingId !== null}
        >
          Refresh
        </button>
      </div>

      {isLoading ? (
        <p className="status-msg" role="status">
          Loading candidates…
        </p>
      ) : (
        <div className="table-container">
          <table className="source-table" aria-label="Candidate sources">
            <thead>
              <tr>
                <th>Source</th>
                <th>Email</th>
                <th>Category</th>
                <th>Signal</th>
                <th>Suggested</th>
                <th>State</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={7} className="empty-row">
                    {candidates.length === 0
                      ? "No review items remain."
                      : "No sources match the current filters."}
                  </td>
                </tr>
              ) : (
                filtered.map((candidate) => (
                  <tr key={candidate.id} className="source-row">
                    <td className="col-source">
                      <span className="source-name">
                        {candidate.sender_name}
                      </span>
                      <span className="source-reason">
                        {candidate.candidate_reason}
                      </span>
                    </td>
                    <td className="col-email">{candidate.sender_email}</td>
                    <td>{candidate.mailbox_category}</td>
                    <td>
                      <span
                        className={`chip chip--signal chip--${candidate.classifier_signal.replace(/_/g, "-")}`}
                      >
                        {signalLabels[candidate.classifier_signal]}
                      </span>
                    </td>
                    <td>
                      <span
                        className={`chip chip--decision chip--${candidate.suggested_decision.replace(/_/g, "-")}`}
                      >
                        {decisionActionLabels[candidate.suggested_decision]}
                      </span>
                    </td>
                    <td>
                      <span
                        className={`chip chip--state chip--${candidate.processing_state.replace(/_/g, "-")}`}
                      >
                        {processingStateLabels[candidate.processing_state]}
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
                            disabled={submittingId === candidate.id}
                            onClick={() => {
                              void handleDecision(candidate.id, decision);
                            }}
                          >
                            {submittingId === candidate.id ? "…" : label}
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
      )}
      <p className="table-footnote">
        No external email actions are executed in this ALPHA. Decisions update
        local state only.
      </p>
    </div>
  );
}
