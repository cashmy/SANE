import { useEffect, useState } from "react";

import { fetchMe, signOut } from "../services/auth";
import type { UserMe } from "../types/auth";
import { AccountMenu } from "./AccountMenu";
import { SignInScreen } from "./SignInScreen";
import { ThemeToggle } from "./ThemeToggle";
import {
  ConnectionsView,
  DecisionsView,
  ReviewView,
  SettingsView,
} from "./views";

type NavKey = "review" | "decisions" | "connections" | "settings";

const navItems: { key: NavKey; label: string }[] = [
  { key: "review", label: "Review" },
  { key: "decisions", label: "Decisions" },
  { key: "connections", label: "Connections" },
  { key: "settings", label: "Settings" },
];

const viewTitles: Record<NavKey, string> = {
  review: "Source Review",
  decisions: "Source Decision History",
  connections: "Connections",
  settings: "Settings",
};

export function AppShell() {
  const [activeView, setActiveView] = useState<NavKey>("review");
  const [user, setUser] = useState<UserMe | null | undefined>(undefined);
  const [isSigningOut, setIsSigningOut] = useState(false);

  useEffect(() => {
    let cancelled = false;

    const loadUser = async () => {
      try {
        const currentUser = await fetchMe();
        if (!cancelled) {
          setUser(currentUser);
        }
      } catch {
        if (!cancelled) {
          setUser(null);
        }
      }
    };

    void loadUser();

    return () => {
      cancelled = true;
    };
  }, []);

  if (user === undefined) {
    return null;
  }

  if (user === null) {
    return (
      <SignInScreen
        onAuthenticated={(signedInUser) => {
          setUser(signedInUser);
        }}
      />
    );
  }

  const handleSignOut = async () => {
    setIsSigningOut(true);
    try {
      await signOut();
    } finally {
      setUser(null);
      setIsSigningOut(false);
    }
  };

  return (
    <div className="app-shell">
      <nav className="sidebar" aria-label="Main navigation">
        <div className="sidebar-brand">SANE</div>
        <ul className="nav-list" role="list">
          {navItems.map(({ key, label }) => (
            <li key={key}>
              <button
                className={`nav-item${activeView === key ? " nav-item--active" : ""}`}
                type="button"
                onClick={() => {
                  setActiveView(key);
                }}
                aria-current={activeView === key ? "page" : undefined}
              >
                {label}
              </button>
            </li>
          ))}
        </ul>
        <div className="sidebar-footer">
          <AccountMenu
            user={user}
            isSigningOut={isSigningOut}
            onSignOut={handleSignOut}
          />
        </div>
      </nav>

      <div className="app-body">
        <header className="toolbar">
          <div className="toolbar-heading">
            <span className="toolbar-kicker">Stage 1 ALPHA</span>
            <h1 className="toolbar-title">{viewTitles[activeView]}</h1>
          </div>
          <div className="toolbar-meta">
            <ThemeToggle />
          </div>
        </header>
        <main className="content-area" aria-label={viewTitles[activeView]}>
          {activeView === "review" && (
            <ReviewView
              isLocalAlpha={user.is_local_alpha}
              onOpenConnections={() => {
                setActiveView("connections");
              }}
            />
          )}
          {activeView === "decisions" && (
            <DecisionsView
              isLocalAlpha={user.is_local_alpha}
              onOpenConnections={() => {
                setActiveView("connections");
              }}
              onOpenReview={() => {
                setActiveView("review");
              }}
            />
          )}
          {activeView === "connections" && <ConnectionsView />}
          {activeView === "settings" && <SettingsView />}
        </main>
      </div>
    </div>
  );
}
