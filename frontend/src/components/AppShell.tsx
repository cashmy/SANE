import { useState } from "react";

import { ThemeToggle } from "./ThemeToggle";
import { ConnectionsView } from "./views/ConnectionsView";
import { DecisionsView } from "./views/DecisionsView";
import { ReviewView } from "./views/ReviewView";
import { SettingsView } from "./views/SettingsView";

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
          <span className="alpha-tag">Stage 1 ALPHA</span>
          <span className="user-placeholder">Local ALPHA User</span>
        </div>
      </nav>

      <div className="app-body">
        <header className="toolbar">
          <div className="toolbar-heading">
            <span className="toolbar-kicker">Stage 1 ALPHA</span>
            <h1 className="toolbar-title">{viewTitles[activeView]}</h1>
          </div>
          <div className="toolbar-meta">
            <span className="toolbar-pill">Local only</span>
            <ThemeToggle />
          </div>
        </header>
        <main className="content-area" aria-label={viewTitles[activeView]}>
          {activeView === "review" && <ReviewView />}
          {activeView === "decisions" && <DecisionsView />}
          {activeView === "connections" && <ConnectionsView />}
          {activeView === "settings" && <SettingsView />}
        </main>
      </div>
    </div>
  );
}
