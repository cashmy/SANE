import { useEffect, useState } from "react";

import { startGmailConnect } from "../../services/auth";
import {
  disconnectGmailAccount,
  listEmailAccounts,
  listIngestionRuns,
  triggerScan,
} from "../../services/api";
import type { EmailAccountInfo, IngestionRunSummary } from "../../types/auth";

const SCAN_LIMIT_OPTIONS = [50, 100, 200] as const;

const formatTimestamp = (value: string | null) => {
  if (!value) {
    return "No timestamp recorded";
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "No timestamp recorded";
  }

  return new Intl.DateTimeFormat("en", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
};

const statusLabel = (status: EmailAccountInfo["connection_status"]) => {
  if (status === "connected") return "Connected";
  if (status === "disconnected") return "Disconnected";
  if (status === "expired") return "Expired";
  if (status === "revoked") return "Revoked";
  if (status === "error") return "Error";
  return "Local only";
};

const statusChipClass = (status: EmailAccountInfo["connection_status"]) => {
  if (status === "connected") return "chip chip--connected";
  if (status === "disconnected") return "chip chip--disconnected";
  if (status === "expired") return "chip chip--warning";
  if (status === "revoked" || status === "error") return "chip chip--danger";
  return "chip chip--neutral";
};

const formatScope = (scope: string) => {
  if (scope === "https://www.googleapis.com/auth/gmail.readonly") {
    return "Gmail read-only";
  }
  return scope;
};

const toErrorMessage = (error: unknown) => {
  if (error instanceof Error) {
    return error.message;
  }
  return "Connections could not be loaded.";
};

export function ConnectionsView() {
  const [accounts, setAccounts] = useState<EmailAccountInfo[]>([]);
  const [runsByAccount, setRunsByAccount] = useState<
    Record<number, IngestionRunSummary[]>
  >({});
  const [selectedLimits, setSelectedLimits] = useState<Record<number, number>>(
    {},
  );
  const [isLoading, setIsLoading] = useState(true);
  const [activeAccountId, setActiveAccountId] = useState<number | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    const loadConnections = async () => {
      setIsLoading(true);
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
        setSelectedLimits((current) => {
          const next = { ...current };
          for (const account of nextAccounts) {
            next[account.id] ??= 50;
          }
          return next;
        });
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

    void loadConnections();

    return () => {
      cancelled = true;
    };
  }, []);

  const handleDisconnect = async (accountId: number) => {
    setActiveAccountId(accountId);
    setErrorMessage(null);
    setStatusMessage(null);

    try {
      await disconnectGmailAccount(accountId);
      setAccounts((current) =>
        current.map((account) =>
          account.id === accountId
            ? {
                ...account,
                connection_status: "disconnected",
                granted_scopes: [],
              }
            : account,
        ),
      );
      setStatusMessage("Gmail disconnected. Existing SANE data was preserved.");
    } catch (error) {
      setErrorMessage(toErrorMessage(error));
    } finally {
      setActiveAccountId(null);
    }
  };

  const handleScan = async (accountId: number) => {
    setActiveAccountId(accountId);
    setErrorMessage(null);
    setStatusMessage(null);

    try {
      const run = await triggerScan({
        email_account_id: accountId,
        limit_count: selectedLimits[accountId] ?? 50,
        scope: "CATEGORY_PROMOTIONS",
      });
      setRunsByAccount((current) => ({
        ...current,
        [accountId]: [run, ...(current[accountId] ?? [])],
      }));
      setStatusMessage(
        `Scan completed: ${run.message_count_scanned} messages checked, ${run.source_count_created} sources created.`,
      );
    } catch (error) {
      setErrorMessage(toErrorMessage(error));
    } finally {
      setActiveAccountId(null);
    }
  };

  return (
    <div className="connections-view" aria-label="Connections">
      <section className="connections-callout">
        <div>
          <h2>Connections</h2>
          <p>
            App sign-in tells SANE who you are. Gmail connection is separate,
            grants read-only mailbox access, and scans only run when you click
            Scan Now.
          </p>
        </div>
        <button
          className="btn-primary"
          type="button"
          onClick={startGmailConnect}
        >
          Connect Gmail
        </button>
      </section>

      {errorMessage ? (
        <div className="alert-error" role="alert">
          {errorMessage}
        </div>
      ) : null}

      {statusMessage ? (
        <p className="status-msg" role="status">
          {statusMessage}
        </p>
      ) : null}

      {isLoading ? <p className="status-msg">Loading connections...</p> : null}

      {!isLoading && accounts.length === 0 ? (
        <section className="placeholder-card">
          <h2>No Gmail accounts connected</h2>
          <p>
            Connect Gmail when you want SANE to scan a mailbox. Until then, no
            Gmail access or ingestion occurs.
          </p>
          <span className="chip chip--neutral">Manual scan only</span>
        </section>
      ) : null}

      {accounts.map((account) => {
        const lastRun = runsByAccount[account.id]?.[0] ?? null;
        const isWorking = activeAccountId === account.id;
        const isConnected = account.connection_status === "connected";

        return (
          <article className="connection-card" key={account.id}>
            <div className="connection-card__header">
              <div>
                <h3>{account.account_email}</h3>
                <p>{account.display_name}</p>
              </div>
              <span className={statusChipClass(account.connection_status)}>
                {statusLabel(account.connection_status)}
              </span>
            </div>

            <dl className="connection-card__meta">
              <div>
                <dt>Granted scope</dt>
                <dd>
                  {account.granted_scopes.length > 0
                    ? account.granted_scopes.map(formatScope).join(", ")
                    : "No scope recorded"}
                </dd>
              </div>
              <div>
                <dt>Last run</dt>
                <dd>
                  {lastRun
                    ? `${lastRun.status} at ${formatTimestamp(lastRun.completed_at ?? lastRun.started_at)}`
                    : "No scan recorded"}
                </dd>
              </div>
            </dl>

            {lastRun ? (
              <div className="connection-run-summary">
                <span className="chip chip--neutral">{lastRun.status}</span>
                <span>
                  {lastRun.message_count_scanned} messages,{" "}
                  {lastRun.source_count_created} sources
                </span>
              </div>
            ) : null}

            <fieldset className="scan-limit-group">
              <legend>Manual scan limit</legend>
              <div className="scan-limit-options">
                {SCAN_LIMIT_OPTIONS.map((limit) => (
                  <label className="scan-limit-option" key={limit}>
                    <input
                      checked={(selectedLimits[account.id] ?? 50) === limit}
                      name={`scan-limit-${account.id}`}
                      onChange={() => {
                        setSelectedLimits((current) => ({
                          ...current,
                          [account.id]: limit,
                        }));
                      }}
                      type="radio"
                      value={limit}
                    />
                    <span>{limit}</span>
                  </label>
                ))}
              </div>
            </fieldset>

            <div className="connection-card__actions">
              {isConnected ? (
                <button
                  className="btn-primary"
                  type="button"
                  onClick={() => {
                    void handleScan(account.id);
                  }}
                  disabled={isWorking}
                >
                  {isWorking ? "Scanning..." : "Scan Now"}
                </button>
              ) : (
                <button
                  className="btn-primary"
                  type="button"
                  onClick={startGmailConnect}
                >
                  Reconnect Gmail
                </button>
              )}

              <button
                className="btn-secondary"
                type="button"
                onClick={() => {
                  void handleDisconnect(account.id);
                }}
                disabled={isWorking || !isConnected}
              >
                Disconnect
              </button>
            </div>
          </article>
        );
      })}
    </div>
  );
}
