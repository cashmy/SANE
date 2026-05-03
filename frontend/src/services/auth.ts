import { ApiError, apiConfig } from "./api";
import type { AuthConfig, UserMe } from "../types/auth";

const getErrorMessage = async (response: Response) => {
  const contentType = response.headers.get("content-type") ?? "";

  if (contentType.includes("application/json")) {
    const payload = (await response.json()) as { detail?: string };
    if (payload.detail) {
      return payload.detail;
    }
  }

  return `Request failed with status ${response.status}`;
};

const requestAuth = async <T>(path: string, init?: RequestInit): Promise<T> => {
  const response = await fetch(`${apiConfig.baseUrl}${path}`, {
    ...init,
    credentials: "include",
    headers: {
      Accept: "application/json",
      ...(init?.headers ?? {}),
    },
  });

  if (!response.ok) {
    throw new ApiError(response.status, await getErrorMessage(response));
  }

  return (await response.json()) as T;
};

export const fetchAuthConfig = () =>
  requestAuth<AuthConfig>(apiConfig.authConfigPath, {
    method: "GET",
  });

export const fetchMe = async (): Promise<UserMe | null> => {
  try {
    const response = await fetch(
      `${apiConfig.baseUrl}${apiConfig.authMePath}`,
      {
        method: "GET",
        credentials: "include",
        headers: {
          Accept: "application/json",
        },
      },
    );

    if (response.status === 401) {
      return null;
    }

    if (!response.ok) {
      throw new ApiError(
        response.status,
        `Request failed with status ${response.status}`,
      );
    }

    return (await response.json()) as UserMe;
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) {
      return null;
    }
    throw error;
  }
};

export const signOut = async () => {
  await fetch(`${apiConfig.baseUrl}${apiConfig.authLogoutPath}`, {
    method: "POST",
    credentials: "include",
  });
};

export const signInAsLocalAlpha = () =>
  requestAuth<UserMe>(apiConfig.authLocalDevLoginPath, {
    method: "POST",
  });

export const startGoogleSignIn = () => {
  window.location.assign(
    `${apiConfig.baseUrl}${apiConfig.authGoogleLoginPath}`,
  );
};

export const startGmailConnect = () => {
  window.location.assign(`${apiConfig.baseUrl}${apiConfig.gmailConnectPath}`);
};
