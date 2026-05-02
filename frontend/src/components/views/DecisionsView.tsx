import { useEffect, useState } from "react";

import { listDecisions } from "../../services/api";
import {
  decisionHistoryLabels,
  type DecisionRecord,
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

  useEffect(() => {
    const load = async () => {
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
    void load();
  }, []);

  return (
    <div className="decisions-view">
      {errorMessage && (
        <div className="alert-error" role="alert">
          {errorMessage}
        </div>
      )}
      {isLoading ? (
        <p className="status-msg" role="status">
          Loading decision history…
        </p>
      ) : (
        <div className="table-container">
          <table className="source-table" aria-label="Decision history">
            <thead>
              <tr>
                <th>Source</th>
                <th>Subject</th>
                <th>Decision</th>
                <th>External action</th>
                <th>Recorded</th>
              </tr>
            </thead>
            <tbody>
              {decisions.length === 0 ? (
                <tr>
                  <td colSpan={5} className="empty-row">
                    No decisions recorded yet.
                  </td>
                </tr>
              ) : (
                decisions.map((d) => (
                  <tr key={d.id} className="source-row">
                    <td className="col-source">
                      <span className="source-name">
                        {d.candidate.sender_name}
                      </span>
                      <span className="source-email">
                        {d.candidate.sender_email}
                      </span>
                    </td>
                    <td>{d.candidate.subject}</td>
                    <td>
                      <span
                        className={`chip chip--decision chip--${d.decision.replace(/_/g, "-")}`}
                      >
                        {decisionHistoryLabels[d.decision]}
                      </span>
                    </td>
                    <td>
                      <span className="chip chip--neutral">Not executed</span>
                    </td>
                    <td className="col-time">
                      {formatTimestamp(d.created_at)}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
