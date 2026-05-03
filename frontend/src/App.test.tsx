import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import App from "./App";
import type {
  EmailAccountInfo,
  IngestionRunSummary,
  UserMe,
} from "./types/auth";
import type {
  DecisionRecord,
  DecisionValue,
  SourceListResponse,
  SourceRow,
  SourceSummary,
} from "./types/workflow";

const localAlphaUser: UserMe = {
  id: 1,
  email: "local-alpha@sane.local",
  display_name: "Local ALPHA User",
  is_local_alpha: true,
};

const seededSources: SourceRow[] = [
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
  {
    id: 2,
    source_key: "routine-platform-bulletin",
    source_name: "Routine Platform Bulletin",
    sender_emails: [
      "bulletin@routine-platform.example",
      "status@routine-platform.example",
      "ops@routine-platform.example",
    ],
    email_count: 41,
    representative_subject: "Monthly status summary for your workspace",
    mailbox_category: "Updates",
    candidate_reason:
      "The source shows some low-value traits, but it remains ambiguous and should stay reviewable.",
    classifier_signal: "ambiguous_source",
    suggested_decision: "keep_for_now",
    current_decision: null,
    confidence: 0.58,
    processing_state: "pending_review",
  },
  {
    id: 3,
    source_key: "workspace-vendor-update",
    source_name: "Workspace Vendor Update",
    sender_emails: [
      "newsletter@workspacevendor.example",
      "events@workspacevendor.example",
    ],
    email_count: 28,
    representative_subject: "April feature digest and customer webinar recap",
    mailbox_category: "Updates",
    candidate_reason:
      "This looks like a recurring update stream that may merit a later unsubscribe decision.",
    classifier_signal: "recurring_updates",
    suggested_decision: "unsubscribe_later",
    current_decision: null,
    confidence: 0.81,
    processing_state: "pending_review",
  },
  {
    id: 4,
    source_key: "founder-network-roundup",
    source_name: "Founder Network Roundup",
    sender_emails: [
      "digest@foundernetwork.example",
      "newsletter@foundernetwork.example",
    ],
    email_count: 22,
    representative_subject:
      "This week in founder communities and partner offers",
    mailbox_category: "Promotions",
    candidate_reason:
      "This looks like a recurring update stream that may merit a later unsubscribe decision.",
    classifier_signal: "recurring_updates",
    suggested_decision: "unsubscribe_later",
    current_decision: null,
    confidence: 0.81,
    processing_state: "pending_review",
  },
  {
    id: 5,
    source_key: "tooling-community-notes",
    source_name: "Tooling Community Notes",
    sender_emails: [
      "notes@tooling-community.example",
      "events@tooling-community.example",
    ],
    email_count: 18,
    representative_subject: "Community office hours and release notes",
    mailbox_category: "Updates",
    candidate_reason:
      "The source shows some low-value traits, but it remains ambiguous and should stay reviewable.",
    classifier_signal: "ambiguous_source",
    suggested_decision: "keep_for_now",
    current_decision: null,
    confidence: 0.58,
    processing_state: "pending_review",
  },
  {
    id: 6,
    source_key: "local-events-weekly",
    source_name: "Local Events Weekly",
    sender_emails: ["weekly@localevents.example"],
    email_count: 13,
    representative_subject: "Neighborhood events newsletter for this week",
    mailbox_category: "Social",
    candidate_reason:
      "This looks like a recurring update stream that may merit a later unsubscribe decision.",
    classifier_signal: "recurring_updates",
    suggested_decision: "unsubscribe_later",
    current_decision: null,
    confidence: 0.81,
    processing_state: "pending_review",
  },
  {
    id: 7,
    source_key: "cloud-billing-notices",
    source_name: "Cloud Billing Notices",
    sender_emails: ["alerts@cloudbilling.example"],
    email_count: 9,
    representative_subject: "Usage threshold reminder and invoice preview",
    mailbox_category: "Updates",
    candidate_reason:
      "The source shows some low-value traits, but it remains ambiguous and should stay reviewable.",
    classifier_signal: "ambiguous_source",
    suggested_decision: "keep_for_now",
    current_decision: null,
    confidence: 0.58,
    processing_state: "pending_review",
  },
  {
    id: 8,
    source_key: "product-research-invitations",
    source_name: "Product Research Invitations",
    sender_emails: ["research@productlab.example"],
    email_count: 6,
    representative_subject: "Invitation to join a short feedback panel",
    mailbox_category: "Updates",
    candidate_reason:
      "The source shows some low-value traits, but it remains ambiguous and should stay reviewable.",
    classifier_signal: "ambiguous_source",
    suggested_decision: "keep_for_now",
    current_decision: null,
    confidence: 0.58,
    processing_state: "pending_review",
  },
];

const cloneSource = (source: SourceRow): SourceRow => ({
  ...source,
  sender_emails: [...source.sender_emails],
});

const toSourceSummary = (source: SourceRow): SourceSummary => ({
  id: source.id,
  source_key: source.source_key,
  source_name: source.source_name,
  sender_emails: [...source.sender_emails],
  email_count: source.email_count,
  representative_subject: source.representative_subject,
  mailbox_category: source.mailbox_category,
  current_decision: source.current_decision,
  processing_state: source.processing_state,
});

const cloneDecision = (decision: DecisionRecord): DecisionRecord => ({
  ...decision,
  source: {
    ...decision.source,
    sender_emails: [...decision.source.sender_emails],
  },
});

const stateForDecision = (
  decision: DecisionValue,
): SourceRow["processing_state"] => {
  if (decision === "keep_for_now") return "kept";
  if (decision === "mark_low_value") return "marked_low_value";
  return "action_recommended";
};

const createMockBackend = (options?: {
  failSources?: boolean;
  unauthenticated?: boolean;
  gmailAccounts?: EmailAccountInfo[];
  gmailRunsByAccount?: Record<number, IngestionRunSummary[]>;
}) => {
  const state = {
    accounts: options?.gmailAccounts ?? [],
    runsByAccount: options?.gmailRunsByAccount ?? {},
    sources: seededSources.map(cloneSource),
    decisions: [] as DecisionRecord[],
    nextDecisionId: 50,
    nextRunId: 1,
  };

  const synchronizeDecisionSourceState = (source: SourceRow) => {
    state.decisions = state.decisions.map((decision) =>
      decision.source.id === source.id
        ? {
            ...decision,
            source: toSourceSummary(source),
          }
        : decision,
    );
  };

  const applyDecision = (
    sourceId: number,
    decision: DecisionValue,
    note?: string,
  ) => {
    const source = state.sources.find((item) => item.id === sourceId);
    if (!source) {
      return jsonResponse({ detail: "Source not found." }, { status: 404 });
    }

    const current = state.decisions.find(
      (entry) => entry.source.id === sourceId && entry.is_current,
    );
    if (current && current.decision === decision) {
      return jsonResponse(cloneDecision(current), { status: 200 });
    }

    if (current) {
      current.is_current = false;
    }

    source.current_decision = decision;
    source.processing_state = stateForDecision(decision);
    synchronizeDecisionSourceState(source);

    const created: DecisionRecord = {
      id: state.nextDecisionId,
      revised_from_decision_id: current?.id ?? null,
      decision,
      note: note ?? null,
      human_confirmed: true,
      external_action_status: "not_executed",
      created_at: new Date(
        Date.UTC(2026, 4, 2, 12, state.nextDecisionId - 50),
      ).toISOString(),
      is_current: true,
      is_revision: Boolean(current),
      source: toSourceSummary(source),
    };
    state.nextDecisionId += 1;
    state.decisions = [created, ...state.decisions];

    return jsonResponse(cloneDecision(created), { status: 201 });
  };

  return async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = new URL(String(input));
    const method = init?.method ?? "GET";

    if (url.pathname === "/api/auth/me" && method === "GET") {
      if (options?.unauthenticated) {
        return jsonResponse(
          { detail: "Authentication required." },
          { status: 401 },
        );
      }

      return jsonResponse(localAlphaUser);
    }

    if (url.pathname === "/api/auth/logout" && method === "POST") {
      return new Response(null, { status: 204 });
    }

    if (url.pathname === "/api/gmail/accounts" && method === "GET") {
      return jsonResponse(state.accounts);
    }

    if (url.pathname.startsWith("/api/gmail/runs/") && method === "GET") {
      const accountId = Number(url.pathname.split("/").at(-1));
      return jsonResponse(state.runsByAccount[accountId] ?? []);
    }

    if (url.pathname === "/api/gmail/disconnect" && method === "POST") {
      const payload = JSON.parse(String(init?.body)) as {
        email_account_id: number;
      };
      state.accounts = state.accounts.map((account) =>
        account.id === payload.email_account_id
          ? {
              ...account,
              connection_status: "disconnected",
              granted_scopes: [],
            }
          : account,
      );
      return new Response(null, { status: 204 });
    }

    if (url.pathname === "/api/gmail/scan" && method === "POST") {
      const payload = JSON.parse(String(init?.body)) as {
        email_account_id: number;
        limit_count: number;
        scope: string;
      };
      const run: IngestionRunSummary = {
        id: state.nextRunId,
        status: "completed",
        scope: payload.scope,
        limit_count: payload.limit_count,
        message_count_scanned: payload.limit_count,
        source_count_created: 2,
        error_summary: null,
        started_at: new Date(
          Date.UTC(2026, 4, 2, 12, state.nextRunId),
        ).toISOString(),
        completed_at: new Date(
          Date.UTC(2026, 4, 2, 12, state.nextRunId, 30),
        ).toISOString(),
      };
      state.nextRunId += 1;
      state.runsByAccount[payload.email_account_id] = [
        run,
        ...(state.runsByAccount[payload.email_account_id] ?? []),
      ];
      return jsonResponse(run);
    }

    if (url.pathname === "/api/sources" && method === "GET") {
      if (options?.failSources) {
        return jsonResponse(
          { detail: "Backend unavailable" },
          {
            status: 500,
          },
        );
      }

      const includeProcessed =
        url.searchParams.get("include_processed") === "true";
      const page = Number(url.searchParams.get("page") ?? "1");
      const pageSize = Number(url.searchParams.get("page_size") ?? "5");
      const search = (url.searchParams.get("search") ?? "").toLowerCase();
      const category = url.searchParams.get("category") ?? "";
      const signal = url.searchParams.get("signal") ?? "";

      const baseFiltered = state.sources.filter((source) => {
        if (!includeProcessed && source.processing_state !== "pending_review") {
          return false;
        }
        if (
          search &&
          !source.source_name.toLowerCase().includes(search) &&
          !source.representative_subject.toLowerCase().includes(search) &&
          !source.sender_emails.join(" ").toLowerCase().includes(search)
        ) {
          return false;
        }
        if (signal && source.classifier_signal !== signal) {
          return false;
        }
        return true;
      });

      const availableCategories = [
        ...new Set(baseFiltered.map((source) => source.mailbox_category)),
      ].sort();

      const filtered = baseFiltered.filter((source) => {
        if (category && source.mailbox_category !== category) {
          return false;
        }
        return true;
      });

      filtered.sort((left, right) => {
        if (right.email_count !== left.email_count) {
          return right.email_count - left.email_count;
        }
        return left.id - right.id;
      });

      const totalItems = filtered.length;
      const totalPages = Math.max(1, Math.ceil(totalItems / pageSize));
      const currentPage = Math.min(page, totalPages);
      const start = (currentPage - 1) * pageSize;
      const items = filtered.slice(start, start + pageSize).map(cloneSource);

      const payload: SourceListResponse = {
        items,
        pagination: {
          page: currentPage,
          page_size: pageSize,
          total_items: totalItems,
          total_pages: totalPages,
          has_previous: currentPage > 1,
          has_next: currentPage < totalPages,
        },
        available_categories: availableCategories,
      };
      return jsonResponse(payload);
    }

    if (url.pathname === "/api/decisions" && method === "GET") {
      return jsonResponse({
        items: state.decisions.map(cloneDecision),
      });
    }

    if (url.pathname === "/api/decisions" && method === "POST") {
      const payload = JSON.parse(String(init?.body)) as {
        source_id: number;
        decision: DecisionValue;
        confirmed: boolean;
        note?: string;
      };

      if (!payload.confirmed) {
        return jsonResponse(
          {
            detail:
              "Explicit human confirmation is required before a decision is recorded.",
          },
          { status: 400 },
        );
      }

      return applyDecision(payload.source_id, payload.decision, payload.note);
    }

    if (url.pathname === "/api/decisions/batch" && method === "POST") {
      const payload = JSON.parse(String(init?.body)) as {
        source_ids: number[];
        decision: DecisionValue;
        confirmed: boolean;
        note?: string;
      };

      if (!payload.confirmed) {
        return jsonResponse(
          {
            detail:
              "Explicit human confirmation is required before a decision is recorded.",
          },
          { status: 400 },
        );
      }

      const uniqueIds = [...new Set(payload.source_ids)];
      const applied: DecisionRecord[] = [];
      const unchanged: DecisionRecord[] = [];

      for (const sourceId of uniqueIds) {
        const response = applyDecision(
          sourceId,
          payload.decision,
          payload.note,
        );
        const decision = (await response.json()) as DecisionRecord;
        if (response.status === 200) {
          unchanged.push(decision);
        } else {
          applied.push(decision);
        }
      }

      return jsonResponse({ applied, unchanged });
    }

    return jsonResponse(
      { detail: `Unhandled request for ${method} ${url.pathname}` },
      { status: 500 },
    );
  };
};

const jsonResponse = (body: unknown, init?: ResponseInit) =>
  new Response(JSON.stringify(body), {
    status: 200,
    headers: {
      "Content-Type": "application/json",
    },
    ...init,
  });

describe("App", () => {
  let consoleErrorSpy: ReturnType<typeof vi.spyOn>;

  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
    vi.stubGlobal(
      "confirm",
      vi.fn(() => true),
    );
    consoleErrorSpy = vi.spyOn(console, "error").mockImplementation(() => {});
  });

  afterEach(() => {
    const output = consoleErrorSpy.mock.calls.flat().join(" ");
    expect(output).not.toMatch(/not wrapped in act/i);
    consoleErrorSpy.mockRestore();
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
    document.documentElement.removeAttribute("data-theme");
    localStorage.removeItem("sane-theme");
  });

  it("renders sidebar navigation, the user placeholder, and the theme toggle", async () => {
    vi.mocked(fetch).mockImplementation(createMockBackend());

    render(<App />);

    await screen.findByRole("table", { name: /source review queue/i });

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
    expect(screen.getByText(/local alpha user/i)).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /switch to dark mode/i }),
    ).toBeInTheDocument();
  });

  it("Review view displays source rows, email count, and approved labels", async () => {
    vi.mocked(fetch).mockImplementation(createMockBackend());

    render(<App />);

    const table = await screen.findByRole("table", {
      name: /source review queue/i,
    });
    expect(
      within(table).getByText(/daily deals dispatch/i),
    ).toBeInTheDocument();
    expect(
      within(table).getByText(/member-perks@dailydeals.example/i),
    ).toBeInTheDocument();
    expect(within(table).getByText("74")).toBeInTheDocument();
    expect(
      within(table).getAllByText(/mark as low value/i).length,
    ).toBeGreaterThan(0);
  });

  it("pagination and page size controls change the displayed sources", async () => {
    vi.mocked(fetch).mockImplementation(createMockBackend());

    render(<App />);

    const table = await screen.findByRole("table", {
      name: /source review queue/i,
    });
    expect(
      within(table).getByText(/daily deals dispatch/i),
    ).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: /next/i }));

    await waitFor(() => {
      expect(screen.getByText(/local events weekly/i)).toBeInTheDocument();
    });
    expect(screen.queryByText(/daily deals dispatch/i)).not.toBeInTheDocument();

    await userEvent.selectOptions(screen.getByLabelText(/page size/i), "10");

    await waitFor(() => {
      expect(
        screen.getByText(/product research invitations/i),
      ).toBeInTheDocument();
    });
    expect(screen.getByText(/page 1 of 1/i)).toBeInTheDocument();
  });

  it("batch decisions require confirmation before updating local state", async () => {
    const confirm = vi
      .fn<() => boolean>()
      .mockReturnValueOnce(false)
      .mockReturnValueOnce(true);
    vi.stubGlobal("confirm", confirm);
    vi.mocked(fetch).mockImplementation(createMockBackend());

    render(<App />);

    await screen.findByRole("table", { name: /source review queue/i });

    await userEvent.click(
      screen.getByRole("checkbox", { name: /select daily deals dispatch/i }),
    );
    await userEvent.click(
      screen.getByRole("checkbox", {
        name: /select routine platform bulletin/i,
      }),
    );

    const batchButton = screen.getByRole("button", {
      name: /apply mark as low value/i,
    });

    await userEvent.click(batchButton);

    expect(confirm).toHaveBeenCalledTimes(1);
    expect(screen.getByText(/daily deals dispatch/i)).toBeInTheDocument();

    await userEvent.click(batchButton);

    await waitFor(() => {
      expect(
        screen.queryByText(/daily deals dispatch/i),
      ).not.toBeInTheDocument();
    });
    expect(confirm).toHaveBeenCalledTimes(2);
    expect(screen.getByRole("status")).toHaveTextContent(/2 sources updated/i);
  });

  it("Decisions view supports explicit source revision", async () => {
    vi.mocked(fetch).mockImplementation(createMockBackend());

    render(<App />);

    const reviewTable = await screen.findByRole("table", {
      name: /source review queue/i,
    });
    const reviewRow = within(reviewTable)
      .getByText(/daily deals dispatch/i)
      .closest("tr");
    expect(reviewRow).not.toBeNull();

    await userEvent.click(
      within(reviewRow as HTMLElement).getByRole("button", {
        name: /mark as low value/i,
      }),
    );

    await userEvent.click(screen.getByRole("button", { name: /decisions/i }));

    const table = await screen.findByRole("table", {
      name: /source decision history/i,
    });

    const currentRow = within(table)
      .getByText(/daily deals dispatch/i)
      .closest("tr");
    expect(currentRow).not.toBeNull();

    await userEvent.click(
      within(currentRow as HTMLElement).getByRole("button", {
        name: /queue for unsubscribe/i,
      }),
    );

    const updatedTable = await screen.findByRole("table", {
      name: /source decision history/i,
    });

    await waitFor(() => {
      expect(
        within(updatedTable).getAllByText(/revision/i).length,
      ).toBeGreaterThan(0);
    });
    expect(
      within(updatedTable).getAllByText(/daily deals dispatch/i).length,
    ).toBeGreaterThan(1);
  });

  it("shows an error state when the source API fails", async () => {
    vi.mocked(fetch).mockImplementation(
      createMockBackend({ failSources: true }),
    );

    render(<App />);

    expect(await screen.findByRole("alert")).toHaveTextContent(
      /backend unavailable/i,
    );
  });

  it("theme toggle is visible in the toolbar and switches display mode", async () => {
    vi.mocked(fetch).mockImplementation(createMockBackend());

    render(<App />);

    await screen.findByRole("table", { name: /source review queue/i });

    const toggle = screen.getByRole("button", { name: /switch to dark mode/i });
    expect(toggle).toBeInTheDocument();

    await userEvent.click(toggle);

    expect(document.documentElement).toHaveAttribute("data-theme", "dark");
    expect(
      screen.getByRole("button", { name: /switch to light mode/i }),
    ).toBeInTheDocument();
  });

  it("renders the sign-in screen when auth returns 401", async () => {
    vi.mocked(fetch).mockImplementation(
      createMockBackend({ unauthenticated: true }),
    );

    render(<App />);

    expect(
      await screen.findByRole("button", { name: /sign in with google/i }),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("table", { name: /source review queue/i }),
    ).not.toBeInTheDocument();
  });

  it("Connections view shows Gmail status and does not scan on render", async () => {
    vi.mocked(fetch).mockImplementation(
      createMockBackend({
        gmailAccounts: [
          {
            id: 42,
            provider: "gmail",
            account_email: "person@gmail.com",
            display_name: "person@gmail.com",
            connection_status: "connected",
            granted_scopes: ["https://www.googleapis.com/auth/gmail.readonly"],
          },
        ],
        gmailRunsByAccount: {
          42: [
            {
              id: 1,
              status: "completed",
              scope: "CATEGORY_PROMOTIONS",
              limit_count: 50,
              message_count_scanned: 50,
              source_count_created: 4,
              error_summary: null,
              started_at: "2026-05-02T17:00:00.000Z",
              completed_at: "2026-05-02T17:01:00.000Z",
            },
          ],
        },
      }),
    );

    render(<App />);

    await screen.findByRole("table", { name: /source review queue/i });
    await userEvent.click(screen.getByRole("button", { name: /connections/i }));

    expect(
      await screen.findByRole("heading", { name: /person@gmail.com/i }),
    ).toBeInTheDocument();
    expect(screen.getByText(/gmail read-only/i)).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /scan now/i }),
    ).toBeInTheDocument();
    expect(
      vi
        .mocked(fetch)
        .mock.calls.some(([input]) =>
          String(input).includes("/api/gmail/scan"),
        ),
    ).toBe(false);
  });
});
