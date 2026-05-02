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

  it("renders review candidates and previous decisions", async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce(jsonResponse({ items: [candidate] }))
      .mockResolvedValueOnce(jsonResponse({ items: [decision] }));

    render(<App />);

    expect(
      screen.getByRole("heading", {
        name: /review likely low-value email sources without executing email actions/i,
      }),
    ).toBeInTheDocument();
    const reviewRegion = screen.getByRole("region", {
      name: /review candidates/i,
    });
    const historyRegion = screen.getByRole("complementary", {
      name: /previous decisions/i,
    });

    await waitFor(() => {
      expect(
        within(reviewRegion).getByText(candidate.subject),
      ).toBeInTheDocument();
    });
    expect(
      within(historyRegion).getByText(decision.candidate.subject),
    ).toBeInTheDocument();
    expect(
      within(screen.getByLabelText(/workflow status summary/i)).getByText(
        "External actions",
      ),
    ).toBeInTheDocument();
  });

  it("updates local history only after an explicit decision click", async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce(jsonResponse({ items: [candidate] }))
      .mockResolvedValueOnce(jsonResponse({ items: [] }))
      .mockResolvedValueOnce(jsonResponse(decision, { status: 201 }));

    render(<App />);

    expect(await screen.findByText(candidate.subject)).toBeInTheDocument();
    const reviewRegion = screen.getByRole("region", {
      name: /review candidates/i,
    });
    const historyRegion = screen.getByRole("complementary", {
      name: /previous decisions/i,
    });

    expect(
      within(historyRegion).queryByText(/marked as low value/i),
    ).not.toBeInTheDocument();

    await userEvent.click(
      screen.getByRole("button", { name: /mark low value/i }),
    );

    await waitFor(() => {
      expect(
        within(reviewRegion).queryByText(candidate.subject),
      ).not.toBeInTheDocument();
    });
    expect(
      within(historyRegion).getByText(/marked as low value/i),
    ).toBeInTheDocument();
    expect(
      within(historyRegion).getByText(/external action: not executed/i),
    ).toBeInTheDocument();
  });

  it("shows an error state when the workflow API fails", async () => {
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
