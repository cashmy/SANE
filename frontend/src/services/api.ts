import type {
  CandidateListResponse,
  DecisionCreateRequest,
  DecisionListResponse,
  DecisionRecord,
} from "../types/workflow";

export const apiConfig = {
  baseUrl: import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000",
  healthPath: "/api/health",
  candidatesPath: "/api/candidates",
  decisionsPath: "/api/decisions",
};

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
    headers: {
      ...defaultHeaders,
      ...(init?.headers ?? {}),
    },
  });

  if (!response.ok) {
    throw new Error(await getApiErrorMessage(response));
  }

  return (await response.json()) as T;
};

export const listCandidates = () =>
  request<CandidateListResponse>(apiConfig.candidatesPath, {
    method: "GET",
  });

export const listDecisions = () =>
  request<DecisionListResponse>(apiConfig.decisionsPath, {
    method: "GET",
  });

export const createDecision = (payload: DecisionCreateRequest) =>
  request<DecisionRecord>(apiConfig.decisionsPath, {
    method: "POST",
    body: JSON.stringify(payload),
  });
