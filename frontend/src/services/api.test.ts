import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
  createBatchDecision,
  createDecision,
  listEmailAccounts,
  listSources,
} from "./api";

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

  it("parses source responses from the backend", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      jsonResponse({
        items: [
          {
            id: 1,
            source_key: "daily-deals-dispatch",
            source_name: "Daily Deals Dispatch",
            sender_emails: [
              "offers@dailydeals.example",
              "member-perks@dailydeals.example",
            ],
            email_count: 74,
            representative_subject:
              "Weekend flash sale and member-only discount roundup",
            mailbox_category: "Promotions",
            candidate_reason:
              "Repeated promotional language suggests this source is mostly marketing noise.",
            classifier_signal: "promotional_digest",
            suggested_decision: "mark_low_value",
            current_decision: null,
            confidence: 0.93,
            processing_state: "pending_review",
          },
        ],
        pagination: {
          page: 2,
          page_size: 10,
          total_items: 18,
          total_pages: 2,
          has_previous: true,
          has_next: false,
        },
        available_categories: ["Promotions", "Updates"],
      }),
    );

    const response = await listSources({
      page: 2,
      pageSize: 10,
      search: "daily deals",
      category: "Promotions",
      signal: "promotional_digest",
    });

    expect(response.items).toHaveLength(1);
    expect(response.items[0].email_count).toBe(74);
    expect(String(vi.mocked(fetch).mock.calls[0][0])).toBe(
      "http://localhost:8000/api/sources?page=2&page_size=10&search=daily+deals&category=Promotions&signal=promotional_digest",
    );
    expect(vi.mocked(fetch).mock.calls[0][1]).toMatchObject({
      credentials: "include",
      method: "GET",
    });
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
        source_id: 2,
        decision: "mark_low_value",
        confirmed: false,
      }),
    ).rejects.toThrow(/human confirmation/i);
  });

  it("posts batch decision payloads to the batch endpoint", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      jsonResponse({
        applied: [],
        unchanged: [],
      }),
    );

    await createBatchDecision({
      source_ids: [1, 2, 3],
      decision: "mark_low_value",
      confirmed: true,
    });

    expect(fetch).toHaveBeenCalledWith(
      "http://localhost:8000/api/decisions/batch",
      expect.objectContaining({
        credentials: "include",
        method: "POST",
        body: JSON.stringify({
          source_ids: [1, 2, 3],
          decision: "mark_low_value",
          confirmed: true,
        }),
      }),
    );
  });

  it("requests Gmail accounts with cookies included", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      jsonResponse([
        {
          id: 12,
          provider: "gmail",
          account_email: "person@gmail.com",
          display_name: "person@gmail.com",
          connection_status: "connected",
          granted_scopes: ["https://www.googleapis.com/auth/gmail.readonly"],
        },
      ]),
    );

    const response = await listEmailAccounts();

    expect(response).toHaveLength(1);
    expect(response[0].account_email).toBe("person@gmail.com");
    expect(fetch).toHaveBeenCalledWith(
      "http://localhost:8000/api/gmail/accounts",
      expect.objectContaining({
        credentials: "include",
        method: "GET",
      }),
    );
  });
});
