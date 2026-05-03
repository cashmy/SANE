import { useEffect, useState } from "react";

import {
  fetchAuthConfig,
  signInAsLocalAlpha,
  startGoogleSignIn,
} from "../services/auth";
import type { AuthConfig, UserMe } from "../types/auth";

const GOOGLE_NOT_READY_MESSAGE =
  "Google OAuth is not configured for this local environment.";
const CLOCK_SKEW_AUTH_ERROR = "device_clock_out_of_sync";
const CLOCK_SKEW_AUTH_ERROR_MESSAGE =
  "Google sign-in could not be completed because this device clock appears out of sync. Sync your system time and try again.";

interface SignInScreenProps {
  onAuthenticated: (user: UserMe) => void;
}

const toErrorMessage = (error: unknown) => {
  if (error instanceof Error) {
    return error.message;
  }
  return "Sign-in could not be started.";
};

const readAuthErrorFromLocation = () => {
  const url = new URL(window.location.href);
  const authError = url.searchParams.get("auth_error");
  if (!authError) {
    return null;
  }

  url.searchParams.delete("auth_error");
  window.history.replaceState(
    {},
    document.title,
    `${url.pathname}${url.search}${url.hash}`,
  );

  if (authError === CLOCK_SKEW_AUTH_ERROR) {
    return CLOCK_SKEW_AUTH_ERROR_MESSAGE;
  }

  return "Google sign-in could not be completed.";
};

export function SignInScreen({ onAuthenticated }: SignInScreenProps) {
  const [authConfig, setAuthConfig] = useState<AuthConfig | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isStartingGoogle, setIsStartingGoogle] = useState(false);
  const [isStartingLocalDev, setIsStartingLocalDev] = useState(false);

  useEffect(() => {
    let cancelled = false;
    const authError = readAuthErrorFromLocation();
    if (authError) {
      setErrorMessage(authError);
    }

    const loadAuthConfig = async () => {
      try {
        const nextConfig = await fetchAuthConfig();
        if (!cancelled) {
          setAuthConfig(nextConfig);
        }
      } catch {
        if (!cancelled) {
          setAuthConfig(null);
        }
      }
    };

    void loadAuthConfig();

    return () => {
      cancelled = true;
    };
  }, []);

  const resolveAuthConfig = async () => {
    if (authConfig) {
      return authConfig;
    }

    const nextConfig = await fetchAuthConfig();
    setAuthConfig(nextConfig);
    return nextConfig;
  };

  const handleGoogleSignIn = async () => {
    setErrorMessage(null);
    setIsStartingGoogle(true);
    try {
      const config = await resolveAuthConfig();
      if (!config.google_oauth_enabled) {
        setErrorMessage(
          config.google_oauth_message ?? GOOGLE_NOT_READY_MESSAGE,
        );
        return;
      }
      startGoogleSignIn();
    } catch (error) {
      setErrorMessage(toErrorMessage(error));
    } finally {
      setIsStartingGoogle(false);
    }
  };

  const handleLocalDevSignIn = async () => {
    setErrorMessage(null);
    setIsStartingLocalDev(true);
    try {
      const user = await signInAsLocalAlpha();
      onAuthenticated(user);
    } catch (error) {
      setErrorMessage(toErrorMessage(error));
    } finally {
      setIsStartingLocalDev(false);
    }
  };

  return (
    <div className="auth-screen">
      <section className="auth-card" aria-label="Sign in to SANE">
        <span className="auth-kicker">Stage 1 ALPHA</span>
        <h1>Sign in to SANE</h1>
        <p>
          Google sign-in authenticates you to SANE. Gmail mailbox access stays a
          separate step in Connections, and scans only run when you trigger
          them.
        </p>

        {errorMessage ? (
          <div className="alert-error" role="alert">
            {errorMessage}
          </div>
        ) : null}

        <div className="auth-card__actions">
          <button
            className="btn-primary"
            type="button"
            onClick={() => {
              void handleGoogleSignIn();
            }}
            disabled={isStartingGoogle}
          >
            {isStartingGoogle
              ? "Starting Google sign-in..."
              : "Sign in with Google"}
          </button>

          {authConfig?.local_dev_enabled ? (
            <button
              className="btn-secondary"
              type="button"
              onClick={() => {
                void handleLocalDevSignIn();
              }}
              disabled={isStartingLocalDev}
            >
              {isStartingLocalDev
                ? "Starting local development session..."
                : "Continue as Local ALPHA User"}
            </button>
          ) : null}
        </div>

        {authConfig?.local_dev_enabled ? (
          <p className="auth-card__note">
            Local development auth is enabled in this environment. Gmail
            authorization remains a separate step in Connections.
          </p>
        ) : null}
      </section>
    </div>
  );
}
