import type {
  BatchDecisionCreateRequest,
  BatchDecisionResponse,
  DecisionCreateRequest,
  DecisionListResponse,
  DecisionRecord,
  CandidateSignal,
  SourceListResponse,
} from "../types/workflow";
import type { EmailAccountInfo, IngestionRunSummary } from "../types/auth";

export const apiConfig = {
  baseUrl: import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000",
  healthPath: "/api/health",
  authConfigPath: "/api/auth/config",
  authMePath: "/api/auth/me",
  authLocalDevLoginPath: "/api/auth/local-dev/login",
  authLogoutPath: "/api/auth/logout",
  authGoogleLoginPath: "/api/auth/google/login",
  sourcesPath: "/api/sources",
  decisionsPath: "/api/decisions",
  gmailAccountsPath: "/api/gmail/accounts",
  gmailConnectPath: "/api/gmail/connect",
  gmailDisconnectPath: "/api/gmail/disconnect",
  gmailScanPath: "/api/gmail/scan",
};

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

const defaultHeaders = {
  Accept: "application/json",
  "Content-Type": "application/json",
};

const getApiErrorMessage = async (response: Response) => {
  const contentType = response.headers.get("content-type") ?? "";

  if (contentType.includes("application/json")) {
    const payload = (await response.json()) as { detail?: string };
    if (payload.detail) {
      return payload.detail;
    }
  }

  return `Request failed with status ${response.status}`;
};

const request = async <T>(path: string, init?: RequestInit): Promise<T> => {
  const response = await fetch(`${apiConfig.baseUrl}${path}`, {
    ...init,
    credentials: "include",
    headers: {
      ...defaultHeaders,
      ...(init?.headers ?? {}),
    },
  });

  if (!response.ok) {
    throw new ApiError(response.status, await getApiErrorMessage(response));
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
};

interface ListSourcesParams {
  page?: number;
  pageSize?: number;
  search?: string;
  category?: string;
  signal?: CandidateSignal;
  includeProcessed?: boolean;
}

const buildQueryString = (params: ListSourcesParams) => {
  const query = new URLSearchParams();

  if (params.page !== undefined) query.set("page", String(params.page));
  if (params.pageSize !== undefined) {
    query.set("page_size", String(params.pageSize));
  }
  if (params.search) query.set("search", params.search);
  if (params.category) query.set("category", params.category);
  if (params.signal) query.set("signal", params.signal);
  if (params.includeProcessed) query.set("include_processed", "true");

  const search = query.toString();
  return search ? `?${search}` : "";
};

export const listSources = (params: ListSourcesParams = {}) =>
  request<SourceListResponse>(
    `${apiConfig.sourcesPath}${buildQueryString(params)}`,
    {
      method: "GET",
    },
  );

export const listDecisions = () =>
  request<DecisionListResponse>(apiConfig.decisionsPath, {
    method: "GET",
  });

export const createDecision = (payload: DecisionCreateRequest) =>
  request<DecisionRecord>(apiConfig.decisionsPath, {
    method: "POST",
    body: JSON.stringify(payload),
  });

export const createBatchDecision = (payload: BatchDecisionCreateRequest) =>
  request<BatchDecisionResponse>(`${apiConfig.decisionsPath}/batch`, {
    method: "POST",
    body: JSON.stringify(payload),
  });

export const listEmailAccounts = () =>
  request<EmailAccountInfo[]>(apiConfig.gmailAccountsPath, {
    method: "GET",
  });

export const listIngestionRuns = (accountId: number) =>
  request<IngestionRunSummary[]>(
    `${apiConfig.gmailAccountsPath.replace("/accounts", "")}/runs/${accountId}`,
    {
      method: "GET",
    },
  );

export const triggerScan = (payload: {
  email_account_id: number;
  limit_count: number;
  scope: string;
}) =>
  request<IngestionRunSummary>(apiConfig.gmailScanPath, {
    method: "POST",
    body: JSON.stringify(payload),
  });

export const disconnectGmailAccount = (emailAccountId: number) =>
  request<void>(apiConfig.gmailDisconnectPath, {
    method: "POST",
    body: JSON.stringify({ email_account_id: emailAccountId }),
  });
