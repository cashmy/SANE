import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { createDecision, listCandidates } from "./api";

const jsonResponse = (body: unknown, init?: ResponseInit) =>
  new Response(JSON.stringify(body), {
    status: 200,
    headers: {
      "Content-Type": "application/json",
    },
    ...init,
  });

describe("workflow api client", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it("parses candidate responses from the backend", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      jsonResponse({
        items: [
          {
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
          },
        ],
      }),
    );

    const response = await listCandidates();

    expect(response.items).toHaveLength(1);
    expect(fetch).toHaveBeenCalledWith(
      "http://localhost:8000/api/candidates",
      expect.objectContaining({
        method: "GET",
      }),
    );
  });

  it("surfaces backend detail messages for rejected decisions", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      jsonResponse(
        {
          detail:
            "Explicit human confirmation is required before a decision is recorded.",
        },
        {
          status: 400,
        },
      ),
    );

    await expect(
      createDecision({
        candidate_id: 2,
        decision: "mark_low_value",
        confirmed: false,
      }),
    ).rejects.toThrow(/human confirmation/i);
  });
});
