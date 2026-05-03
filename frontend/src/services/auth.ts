import { ApiError, apiConfig } from "./api";
import type { UserMe } from "../types/auth";

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

export const startGoogleSignIn = () => {
  window.location.assign(
    `${apiConfig.baseUrl}${apiConfig.authGoogleLoginPath}`,
  );
};

export const startGmailConnect = () => {
  window.location.assign(`${apiConfig.baseUrl}${apiConfig.gmailConnectPath}`);
};
