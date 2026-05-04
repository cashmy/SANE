import type { Page, Route } from "@playwright/test";

import type {
  AuthConfig,
  EmailAccountInfo,
  IngestionRunSummary,
  ResetLocalDataSummary,
  UserMe,
} from "../../src/types/auth";
import type {
  DecisionListResponse,
  DecisionRecord,
  DecisionValue,
  SourceListResponse,
  SourceRow,
  SourceSummary,
} from "../../src/types/workflow";

type ScenarioName = "local-dev-auth" | "mailbox";

interface RecordedRequest {
  method: string;
  pathname: string;
  search: string;
}

interface MockState {
  authConfig: AuthConfig;
  currentUser: UserMe | null;
  accounts: EmailAccountInfo[];
  runsByAccount: Record<number, IngestionRunSummary[]>;
  sources: SourceRow[];
  sourceAccountIds: Record<number, number>;
  decisions: DecisionRecord[];
  nextDecisionId: number;
  nextRunId: number;
}

export interface MockApiController {
  requests: RecordedRequest[];
  countRequests: (pathname: string, method?: string) => number;
}

const localAlphaUser: UserMe = {
  id: 1,
  email: "local-alpha@sane.local",
  display_name: "Local ALPHA User",
  is_local_alpha: true,
};

const signedInUser: UserMe = {
  id: 2,
  email: "person@example.com",
  display_name: "Person Example",
  is_local_alpha: false,
};

const localDevAuthConfig: AuthConfig = {
  auth_mode: "local_dev",
  local_dev_enabled: true,
  google_oauth_enabled: false,
  google_oauth_message:
    "Google OAuth is not configured for this local environment.",
};

const googleAuthConfig: AuthConfig = {
  auth_mode: "google_oauth",
  local_dev_enabled: false,
  google_oauth_enabled: true,
  google_oauth_message: null,
};

const mailboxAccount: EmailAccountInfo = {
  id: 2,
  provider: "gmail",
  account_email: "alpha.mailbox@example.com",
  display_name: "Alpha Mailbox",
  connection_status: "connected",
  granted_scopes: ["https://www.googleapis.com/auth/gmail.readonly"],
};

const mailboxRun: IngestionRunSummary = {
  id: 301,
  status: "completed",
  scope: "CATEGORY_PROMOTIONS",
  limit_count: 50,
  message_count_scanned: 50,
  source_count_seen: 31,
  source_count_created: 9,
  error_summary: null,
  started_at: "2026-05-03T18:00:00.000Z",
  completed_at: "2026-05-03T18:01:00.000Z",
};

const buildPendingSource = (
  id: number,
  sourceKey: string,
  sourceName: string,
  senderEmails: string[],
  emailCount: number,
  representativeSubject: string,
  mailboxCategory: string,
  candidateReason: string,
  classifierSignal: SourceRow["classifier_signal"],
  suggestedDecision: SourceRow["suggested_decision"],
): SourceRow => ({
  id,
  source_key: sourceKey,
  source_name: sourceName,
  sender_emails: senderEmails,
  email_count: emailCount,
  representative_subject: representativeSubject,
  mailbox_category: mailboxCategory,
  candidate_reason: candidateReason,
  classifier_signal: classifierSignal,
  suggested_decision: suggestedDecision,
  current_decision: null,
  confidence: 0.81,
  processing_state: "pending_review",
});

const buildResolvedSource = (
  id: number,
  sourceKey: string,
  sourceName: string,
  senderEmails: string[],
  emailCount: number,
  representativeSubject: string,
  mailboxCategory: string,
  currentDecision: DecisionValue,
  processingState: SourceRow["processing_state"],
): SourceRow => ({
  id,
  source_key: sourceKey,
  source_name: sourceName,
  sender_emails: senderEmails,
  email_count: emailCount,
  representative_subject: representativeSubject,
  mailbox_category: mailboxCategory,
  candidate_reason:
    "This source already has local decision history and should stay visible in Decisions only.",
  classifier_signal: "recurring_updates",
  suggested_decision: currentDecision,
  current_decision: currentDecision,
  confidence: 0.88,
  processing_state: processingState,
});

const localReviewSources: SourceRow[] = [
  buildPendingSource(
    11,
    "daily-deals-dispatch",
    "Daily Deals Dispatch",
    ["offers@dailydeals.example", "member-perks@dailydeals.example"],
    74,
    "Weekend flash sale and member-only discount roundup",
    "Promotions",
    "Observed promotional cues in stored metadata: 'deal', 'sale', and 'discount'. Suggest marking this source as low value, while keeping the final decision human-reviewed.",
    "promotional_digest",
    "mark_low_value",
  ),
  buildPendingSource(
    12,
    "routine-platform-bulletin",
    "Routine Platform Bulletin",
    ["bulletin@routine-platform.example", "status@routine-platform.example"],
    41,
    "Monthly status summary for your workspace",
    "Updates",
    "Observed evidence is limited or mixed in stored metadata: 'bulletin' and 'monthly'. Keep Source for now until a human reviews the source.",
    "ambiguous_source",
    "keep_for_now",
  ),
  buildPendingSource(
    13,
    "workspace-vendor-update",
    "Workspace Vendor Update",
    ["newsletter@workspacevendor.example", "events@workspacevendor.example"],
    28,
    "April feature digest and customer webinar recap",
    "Updates",
    "Observed recurring list cues in stored metadata: 'newsletter', 'digest', and 'recap'. Queue for Unsubscribe may be worth human review.",
    "recurring_updates",
    "unsubscribe_later",
  ),
  buildPendingSource(
    14,
    "founder-network-roundup",
    "Founder Network Roundup",
    ["digest@foundernetwork.example", "newsletter@foundernetwork.example"],
    22,
    "This week in founder communities and partner offers",
    "Promotions",
    "Observed recurring list cues in stored metadata: 'roundup' and 'digest'. Queue for Unsubscribe may be worth human review.",
    "recurring_updates",
    "unsubscribe_later",
  ),
  buildPendingSource(
    15,
    "tooling-community-notes",
    "Tooling Community Notes",
    ["notes@tooling-community.example", "events@tooling-community.example"],
    18,
    "Community office hours and release notes",
    "Updates",
    "Observed evidence is limited or mixed in stored metadata: 'release notes' and 'community notes'. Keep Source for now until a human reviews the source.",
    "ambiguous_source",
    "keep_for_now",
  ),
  buildPendingSource(
    16,
    "local-events-weekly",
    "Local Events Weekly",
    ["weekly@localevents.example"],
    13,
    "Neighborhood events newsletter for this week",
    "Social",
    "Observed recurring list cues in stored metadata: 'newsletter' and 'weekly'. Queue for Unsubscribe may be worth human review.",
    "recurring_updates",
    "unsubscribe_later",
  ),
  buildPendingSource(
    17,
    "cloud-billing-notices",
    "Cloud Billing Notices",
    ["alerts@cloudbilling.example"],
    9,
    "Usage threshold reminder and invoice preview",
    "Updates",
    "Observed cautionary metadata that can indicate transactional or account-related email: 'invoice', 'billing', and 'usage threshold'. Keep Source for now and review it locally before taking any stronger action.",
    "ambiguous_source",
    "keep_for_now",
  ),
];

const mailboxPendingSources: SourceRow[] = [
  buildPendingSource(
    101,
    "daily-deals-dispatch",
    "Daily Deals Dispatch",
    ["offers@dailydeals.example", "member-perks@dailydeals.example"],
    74,
    "Weekend flash sale and member-only discount roundup",
    "Promotions",
    "Observed promotional cues in stored metadata: 'deal', 'sale', and 'discount'. Suggest marking this source as low value, while keeping the final decision human-reviewed.",
    "promotional_digest",
    "mark_low_value",
  ),
  buildPendingSource(
    102,
    "routine-platform-bulletin",
    "Routine Platform Bulletin",
    ["bulletin@routine-platform.example", "status@routine-platform.example"],
    41,
    "Monthly status summary for your workspace",
    "Updates",
    "Observed evidence is limited or mixed in stored metadata: 'bulletin' and 'monthly'. Keep Source for now until a human reviews the source.",
    "ambiguous_source",
    "keep_for_now",
  ),
  buildPendingSource(
    103,
    "workspace-vendor-update",
    "Workspace Vendor Update",
    ["newsletter@workspacevendor.example", "events@workspacevendor.example"],
    28,
    "April feature digest and customer webinar recap",
    "Updates",
    "Observed recurring list cues in stored metadata: 'newsletter', 'digest', and 'recap'. Queue for Unsubscribe may be worth human review.",
    "recurring_updates",
    "unsubscribe_later",
  ),
  buildPendingSource(
    104,
    "founder-network-roundup",
    "Founder Network Roundup",
    ["digest@foundernetwork.example", "newsletter@foundernetwork.example"],
    22,
    "This week in founder communities and partner offers",
    "Promotions",
    "Observed recurring list cues in stored metadata: 'roundup' and 'digest'. Queue for Unsubscribe may be worth human review.",
    "recurring_updates",
    "unsubscribe_later",
  ),
  buildPendingSource(
    105,
    "tooling-community-notes",
    "Tooling Community Notes",
    ["notes@tooling-community.example", "events@tooling-community.example"],
    18,
    "Community office hours and release notes",
    "Updates",
    "Observed evidence is limited or mixed in stored metadata: 'release notes' and 'community notes'. Keep Source for now until a human reviews the source.",
    "ambiguous_source",
    "keep_for_now",
  ),
  buildPendingSource(
    106,
    "local-events-weekly",
    "Local Events Weekly",
    ["weekly@localevents.example"],
    13,
    "Neighborhood events newsletter for this week",
    "Social",
    "Observed recurring list cues in stored metadata: 'newsletter' and 'weekly'. Queue for Unsubscribe may be worth human review.",
    "recurring_updates",
    "unsubscribe_later",
  ),
  buildPendingSource(
    107,
    "cloud-billing-notices",
    "Cloud Billing Notices",
    ["alerts@cloudbilling.example"],
    9,
    "Usage threshold reminder and invoice preview",
    "Updates",
    "Observed cautionary metadata that can indicate transactional or account-related email: 'invoice', 'billing', and 'usage threshold'. Keep Source for now and review it locally before taking any stronger action.",
    "ambiguous_source",
    "keep_for_now",
  ),
];

const mailboxHistorySources: SourceRow[] = [
  buildResolvedSource(
    201,
    "partner-digest-weekly",
    "Partner Digest Weekly",
    ["digest@partnerweekly.example"],
    12,
    "Partner offers and channel updates",
    "Promotions",
    "unsubscribe_later",
    "action_recommended",
  ),
  buildResolvedSource(
    202,
    "creator-platform-alerts",
    "Creator Platform Alerts",
    ["alerts@creatorplatform.example"],
    8,
    "Campaign summary and creator insights",
    "Updates",
    "mark_low_value",
    "marked_low_value",
  ),
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

const buildDecision = (
  id: number,
  source: SourceRow,
  decision: DecisionValue,
  createdAt: string,
  isCurrent: boolean,
  isRevision: boolean,
  revisedFromDecisionId: number | null,
): DecisionRecord => ({
  id,
  revised_from_decision_id: revisedFromDecisionId,
  decision,
  note: null,
  human_confirmed: true,
  external_action_status: "not_executed",
  created_at: createdAt,
  is_current: isCurrent,
  is_revision: isRevision,
  source: toSourceSummary(source),
});

const buildMailboxDecisions = (sources: SourceRow[]): DecisionRecord[] => {
  const first = sources.find((source) => source.id === 201);
  const second = sources.find((source) => source.id === 202);

  if (!first || !second) {
    return [];
  }

  return [
    buildDecision(
      606,
      second,
      "mark_low_value",
      "2026-05-03T18:42:00.000Z",
      true,
      true,
      605,
    ),
    buildDecision(
      603,
      first,
      "unsubscribe_later",
      "2026-05-03T18:41:00.000Z",
      true,
      true,
      602,
    ),
    buildDecision(
      605,
      second,
      "keep_for_now",
      "2026-05-03T18:34:00.000Z",
      false,
      true,
      604,
    ),
    buildDecision(
      602,
      first,
      "mark_low_value",
      "2026-05-03T18:33:00.000Z",
      false,
      true,
      601,
    ),
    buildDecision(
      604,
      second,
      "unsubscribe_later",
      "2026-05-03T18:12:00.000Z",
      false,
      false,
      null,
    ),
    buildDecision(
      601,
      first,
      "keep_for_now",
      "2026-05-03T18:11:00.000Z",
      false,
      false,
      null,
    ),
  ];
};

const buildScenarioState = (scenario: ScenarioName): MockState => {
  if (scenario === "local-dev-auth") {
    const sources = localReviewSources.map(cloneSource);
    return {
      authConfig: localDevAuthConfig,
      currentUser: null,
      accounts: [],
      runsByAccount: {},
      sources,
      sourceAccountIds: Object.fromEntries(
        sources.map((source) => [source.id, 1]),
      ) as Record<number, number>,
      decisions: [],
      nextDecisionId: 501,
      nextRunId: 1,
    };
  }

  const sources = [...mailboxPendingSources, ...mailboxHistorySources].map(
    cloneSource,
  );

  return {
    authConfig: googleAuthConfig,
    currentUser: signedInUser,
    accounts: [{ ...mailboxAccount }],
    runsByAccount: {
      [mailboxAccount.id]: [{ ...mailboxRun }],
    },
    sources,
    sourceAccountIds: Object.fromEntries(
      sources.map((source) => [source.id, mailboxAccount.id]),
    ) as Record<number, number>,
    decisions: buildMailboxDecisions(sources).map(cloneDecision),
    nextDecisionId: 607,
    nextRunId: 302,
  };
};

const parseOptionalNumber = (value: string | null) => {
  if (!value) return null;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
};

const parseBody = <T>(route: Route): T => {
  const payload = route.request().postData();
  return JSON.parse(payload ?? "{}") as T;
};

const fulfillJson = (route: Route, payload: unknown, status = 200) =>
  route.fulfill({
    status,
    contentType: "application/json",
    body: JSON.stringify(payload),
  });

const fulfillEmpty = (route: Route, status = 204) =>
  route.fulfill({
    status,
  });

export const installSaneMockApi = async (
  page: Page,
  scenario: ScenarioName,
): Promise<MockApiController> => {
  const state = buildScenarioState(scenario);
  const requests: RecordedRequest[] = [];

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

  const applyDecision = (sourceId: number, decision: DecisionValue) => {
    const source = state.sources.find((item) => item.id === sourceId);
    if (!source) {
      return {
        status: 404,
        payload: { detail: "Source not found." },
      };
    }

    const current = state.decisions.find(
      (entry) => entry.source.id === sourceId && entry.is_current,
    );

    if (current && current.decision === decision) {
      return {
        status: 200,
        payload: cloneDecision(current),
      };
    }

    if (current) {
      current.is_current = false;
    }

    source.current_decision = decision;
    source.processing_state = stateForDecision(decision);
    synchronizeDecisionSourceState(source);

    const created = buildDecision(
      state.nextDecisionId,
      source,
      decision,
      new Date(
        Date.UTC(2026, 4, 3, 19, state.nextDecisionId - 600),
      ).toISOString(),
      true,
      Boolean(current),
      current?.id ?? null,
    );
    state.nextDecisionId += 1;
    state.decisions = [created, ...state.decisions];

    return {
      status: 201,
      payload: cloneDecision(created),
    };
  };

  await page.route("**/api/**", async (route) => {
    const request = route.request();
    const url = new URL(request.url());
    const method = request.method();

    requests.push({
      method,
      pathname: url.pathname,
      search: url.search,
    });

    if (method === "OPTIONS") {
      await fulfillEmpty(route);
      return;
    }

    if (url.pathname === "/api/health" && method === "GET") {
      await fulfillJson(route, { status: "ok" });
      return;
    }

    if (url.pathname === "/api/auth/config" && method === "GET") {
      await fulfillJson(route, state.authConfig);
      return;
    }

    if (url.pathname === "/api/auth/me" && method === "GET") {
      if (!state.currentUser) {
        await fulfillJson(route, { detail: "Authentication required." }, 401);
        return;
      }

      await fulfillJson(route, state.currentUser);
      return;
    }

    if (url.pathname === "/api/auth/local-dev/login" && method === "POST") {
      if (!state.authConfig.local_dev_enabled) {
        await fulfillJson(
          route,
          { detail: "Local development auth is not enabled." },
          404,
        );
        return;
      }

      state.currentUser = localAlphaUser;
      await fulfillJson(route, localAlphaUser);
      return;
    }

    if (url.pathname === "/api/auth/logout" && method === "POST") {
      state.currentUser = null;
      await fulfillEmpty(route);
      return;
    }

    if (!state.currentUser) {
      await fulfillJson(route, { detail: "Authentication required." }, 401);
      return;
    }

    if (url.pathname === "/api/gmail/accounts" && method === "GET") {
      await fulfillJson(route, state.accounts);
      return;
    }

    if (url.pathname.startsWith("/api/gmail/runs/") && method === "GET") {
      const accountId = Number(url.pathname.split("/").at(-1));
      await fulfillJson(route, state.runsByAccount[accountId] ?? []);
      return;
    }

    if (url.pathname === "/api/gmail/disconnect" && method === "POST") {
      const payload = parseBody<{ email_account_id: number }>(route);
      state.accounts = state.accounts.map((account) =>
        account.id === payload.email_account_id
          ? {
              ...account,
              connection_status: "disconnected",
              granted_scopes: [],
            }
          : account,
      );
      await fulfillEmpty(route);
      return;
    }

    if (
      /^\/api\/gmail\/accounts\/\d+\/reset-local-data$/.test(url.pathname) &&
      method === "POST"
    ) {
      const accountId = Number(url.pathname.split("/").at(-2));
      const payload = parseBody<{
        mode: "sources_only" | "sources_and_decisions";
        confirmed: boolean;
      }>(route);

      if (!payload.confirmed) {
        await fulfillJson(
          route,
          {
            detail:
              "Explicit human confirmation is required before local data reset.",
          },
          400,
        );
        return;
      }

      if (payload.mode === "sources_only") {
        await fulfillJson(
          route,
          {
            detail:
              "Current ALPHA data model cannot preserve decisions when sources are deleted.",
          },
          400,
        );
        return;
      }

      const account = state.accounts.find((entry) => entry.id === accountId);
      const sourceIds = Object.entries(state.sourceAccountIds)
        .filter(([, mappedAccountId]) => mappedAccountId === accountId)
        .map(([sourceId]) => Number(sourceId));
      const sourceIdSet = new Set(sourceIds);
      const summary: ResetLocalDataSummary = {
        account_id: accountId,
        account_email: account?.account_email ?? "unknown@example.com",
        mode: "sources_and_decisions",
        sources_deleted: state.sources.filter((source) =>
          sourceIdSet.has(source.id),
        ).length,
        decisions_deleted: state.decisions.filter((decision) =>
          sourceIdSet.has(decision.source.id),
        ).length,
        ingestion_runs_preserved: state.runsByAccount[accountId]?.length ?? 0,
        ingestion_runs_deleted: 0,
      };

      state.sources = state.sources.filter(
        (source) => !sourceIdSet.has(source.id),
      );
      state.decisions = state.decisions.filter(
        (decision) => !sourceIdSet.has(decision.source.id),
      );

      await fulfillJson(route, summary);
      return;
    }

    if (url.pathname === "/api/gmail/scan" && method === "POST") {
      const payload = parseBody<{
        email_account_id: number;
        limit_count: number;
        scope: string;
      }>(route);
      const run: IngestionRunSummary = {
        id: state.nextRunId,
        status: "completed",
        scope: payload.scope,
        limit_count: payload.limit_count,
        message_count_scanned: payload.limit_count,
        source_count_seen: 2,
        source_count_created: 2,
        error_summary: null,
        started_at: new Date(
          Date.UTC(2026, 4, 3, 20, state.nextRunId),
        ).toISOString(),
        completed_at: new Date(
          Date.UTC(2026, 4, 3, 20, state.nextRunId, 30),
        ).toISOString(),
      };
      state.nextRunId += 1;
      state.runsByAccount[payload.email_account_id] = [
        run,
        ...(state.runsByAccount[payload.email_account_id] ?? []),
      ];
      await fulfillJson(route, run);
      return;
    }

    if (url.pathname === "/api/sources" && method === "GET") {
      const includeProcessed =
        url.searchParams.get("include_processed") === "true";
      const pageNumber = Number(url.searchParams.get("page") ?? "1");
      const pageSize = Number(url.searchParams.get("page_size") ?? "5");
      const emailAccountId = parseOptionalNumber(
        url.searchParams.get("email_account_id"),
      );
      const search = (url.searchParams.get("search") ?? "").toLowerCase();
      const category = url.searchParams.get("category") ?? "";
      const signal = url.searchParams.get("signal") ?? "";

      const baseFiltered = state.sources.filter((source) => {
        if (
          emailAccountId !== null &&
          state.sourceAccountIds[source.id] !== emailAccountId
        ) {
          return false;
        }
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
      const currentPage = Math.min(pageNumber, totalPages);
      const start = (currentPage - 1) * pageSize;
      const payload: SourceListResponse = {
        items: filtered.slice(start, start + pageSize).map(cloneSource),
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
      await fulfillJson(route, payload);
      return;
    }

    if (url.pathname === "/api/decisions" && method === "GET") {
      const pageNumber = Number(url.searchParams.get("page") ?? "1");
      const pageSize = Number(url.searchParams.get("page_size") ?? "5");
      const emailAccountId = parseOptionalNumber(
        url.searchParams.get("email_account_id"),
      );
      const filtered = state.decisions.filter((decision) => {
        if (emailAccountId === null) {
          return true;
        }
        return state.sourceAccountIds[decision.source.id] === emailAccountId;
      });
      const totalItems = filtered.length;
      const totalPages = Math.max(1, Math.ceil(totalItems / pageSize));
      const currentPage = Math.min(pageNumber, totalPages);
      const start = (currentPage - 1) * pageSize;
      const payload: DecisionListResponse = {
        items: filtered.slice(start, start + pageSize).map(cloneDecision),
        pagination: {
          page: currentPage,
          page_size: pageSize,
          total_items: totalItems,
          total_pages: totalPages,
          has_previous: currentPage > 1,
          has_next: currentPage < totalPages,
        },
      };
      await fulfillJson(route, payload);
      return;
    }

    if (url.pathname === "/api/decisions" && method === "POST") {
      const payload = parseBody<{
        source_id: number;
        decision: DecisionValue;
        confirmed: boolean;
      }>(route);

      if (!payload.confirmed) {
        await fulfillJson(
          route,
          {
            detail:
              "Explicit human confirmation is required before a decision is recorded.",
          },
          400,
        );
        return;
      }

      const result = applyDecision(payload.source_id, payload.decision);
      await fulfillJson(route, result.payload, result.status);
      return;
    }

    if (url.pathname === "/api/decisions/batch" && method === "POST") {
      const payload = parseBody<{
        source_ids: number[];
        decision: DecisionValue;
        confirmed: boolean;
      }>(route);

      if (!payload.confirmed) {
        await fulfillJson(
          route,
          {
            detail:
              "Explicit human confirmation is required before a decision is recorded.",
          },
          400,
        );
        return;
      }

      const uniqueIds = [...new Set(payload.source_ids)];
      const applied: DecisionRecord[] = [];
      const unchanged: DecisionRecord[] = [];

      for (const sourceId of uniqueIds) {
        const result = applyDecision(sourceId, payload.decision);
        const decision = result.payload as DecisionRecord;
        if (result.status === 200) {
          unchanged.push(decision);
        } else if (result.status === 201) {
          applied.push(decision);
        }
      }

      await fulfillJson(route, {
        applied,
        unchanged,
      });
      return;
    }

    await fulfillJson(
      route,
      {
        detail: `Unhandled mock API route: ${method} ${url.pathname}`,
      },
      501,
    );
  });

  return {
    requests,
    countRequests: (pathname: string, method?: string) =>
      requests.filter(
        (request) =>
          request.pathname === pathname &&
          (method === undefined || request.method === method),
      ).length,
  };
};
