import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import App from "./App";

const candidate = {
  id: 1,
  sender_name: "Daily Deals Dispatch",
  sender_email: "offers@dailydeals.example",
  subject: "Weekend flash sale and member-only discount roundup",
  mailbox_category: "Promotions",
  candidate_reason:
    "Repeated promotional language suggests this source is mostly marketing noise.",
  classifier_signal: "promotional_digest",
  suggested_decision: "mark_low_value",
  confidence: 0.93,
  processing_state: "pending_review",
} as const;

const decision = {
  id: 4,
  decision: "mark_low_value",
  note: null,
  human_confirmed: true,
  external_action_status: "not_executed",
  created_at: "2026-05-02T12:00:00Z",
  candidate: {
    id: 1,
    sender_name: "Daily Deals Dispatch",
    sender_email: "offers@dailydeals.example",
    subject: "Weekend flash sale and member-only discount roundup",
    processing_state: "marked_low_value",
  },
} as const;

const jsonResponse = (body: unknown, init?: ResponseInit) =>
  new Response(JSON.stringify(body), {
    status: 200,
    headers: {
      "Content-Type": "application/json",
    },
    ...init,
  });

describe("App", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it("renders sidebar navigation with all four views", () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce(jsonResponse({ items: [] }))
      .mockResolvedValueOnce(jsonResponse({ items: [] }));

    render(<App />);

    const nav = screen.getByRole("navigation", { name: /main navigation/i });
    expect(
      within(nav).getByRole("button", { name: /review/i }),
    ).toBeInTheDocument();
    expect(
      within(nav).getByRole("button", { name: /decisions/i }),
    ).toBeInTheDocument();
    expect(
      within(nav).getByRole("button", { name: /connections/i }),
    ).toBeInTheDocument();
    expect(
      within(nav).getByRole("button", { name: /settings/i }),
    ).toBeInTheDocument();
  });

  it("Review view displays candidate source rows", async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce(jsonResponse({ items: [candidate] }))
      .mockResolvedValueOnce(jsonResponse({ items: [] }));

    render(<App />);

    const table = await screen.findByRole("table", {
      name: /candidate sources/i,
    });
    expect(within(table).getByText(candidate.sender_name)).toBeInTheDocument();
    expect(within(table).getByText(candidate.sender_email)).toBeInTheDocument();
  });

  it("Decisions view is separate from Review view", async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce(jsonResponse({ items: [candidate] }))
      .mockResolvedValueOnce(jsonResponse({ items: [] }))
      .mockResolvedValueOnce(jsonResponse({ items: [decision] }));

    render(<App />);

    await screen.findByRole("table", { name: /candidate sources/i });

    await userEvent.click(screen.getByRole("button", { name: /decisions/i }));

    const decisionsTable = await screen.findByRole("table", {
      name: /decision history/i,
    });
    expect(
      within(decisionsTable).getByText(/marked as low value/i),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("table", { name: /candidate sources/i }),
    ).not.toBeInTheDocument();
  });

  it("decision controls require explicit user action and move item from review queue", async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce(jsonResponse({ items: [candidate] }))
      .mockResolvedValueOnce(jsonResponse({ items: [] }))
      .mockResolvedValueOnce(jsonResponse(decision, { status: 201 }));

    render(<App />);

    await screen.findByText(candidate.sender_name);

    await userEvent.click(
      screen.getByRole("button", { name: /mark low value/i }),
    );

    await waitFor(() => {
      expect(screen.queryByText(candidate.sender_name)).not.toBeInTheDocument();
    });
  });

  it("Decisions view shows external action status as not executed", async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce(jsonResponse({ items: [] }))
      .mockResolvedValueOnce(jsonResponse({ items: [] }))
      .mockResolvedValueOnce(jsonResponse({ items: [decision] }));

    render(<App />);

    await userEvent.click(screen.getByRole("button", { name: /decisions/i }));

    const table = await screen.findByRole("table", {
      name: /decision history/i,
    });
    expect(within(table).getAllByText(/not executed/i).length).toBeGreaterThan(
      0,
    );
  });

  it("shows an error state when the Review API fails", async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce(
        jsonResponse(
          { detail: "Backend unavailable" },
          {
            status: 500,
          },
        ),
      )
      .mockResolvedValueOnce(jsonResponse({ items: [] }));

    render(<App />);

    expect(await screen.findByRole("alert")).toHaveTextContent(
      /backend unavailable/i,
    );
  });
});
