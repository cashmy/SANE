import { expect, test } from "@playwright/test";

import { installSaneMockApi } from "./fixtures/saneMockApi";

test.describe("SANE Playwright smoke foundation", () => {
  test("local-dev auth enters the app shell and navigates views", async ({
    page,
  }) => {
    const mockApi = await installSaneMockApi(page, "local-dev-auth");

    await page.goto("/");

    await expect(
      page.getByRole("heading", { name: "Sign in to SANE" }),
    ).toBeVisible();
    await expect(
      page.getByRole("button", { name: "Continue as Local ALPHA User" }),
    ).toBeVisible();

    await page
      .getByRole("button", { name: "Continue as Local ALPHA User" })
      .click();

    const review = page.getByRole("main", { name: "Source Review" });
    await expect(review).toBeVisible();
    await expect(
      review.getByRole("table", { name: "Source review queue" }),
    ).toBeVisible();
    await expect(review.getByText("Daily Deals Dispatch")).toBeVisible();

    await page.getByRole("button", { name: "Decisions" }).click();
    const decisions = page.getByRole("main", {
      name: "Source Decision History",
    });
    await expect(decisions).toBeVisible();
    await expect(
      decisions.getByText("No local decisions recorded yet"),
    ).toBeVisible();

    await page.getByRole("button", { name: "Connections" }).click();
    const connections = page.getByRole("main", { name: "Connections" });
    await expect(connections).toBeVisible();
    await expect(
      connections.getByText("No Gmail accounts connected"),
    ).toBeVisible();

    expect(mockApi.countRequests("/api/auth/local-dev/login", "POST")).toBe(1);
  });

  test("Connections safety copy and reset cancel path stay local-only", async ({
    page,
  }) => {
    const mockApi = await installSaneMockApi(page, "mailbox");

    await page.goto("/");
    await page.getByRole("button", { name: "Connections" }).click();

    const connections = page.getByRole("main", { name: "Connections" });
    await expect(connections).toBeVisible();
    await expect(
      connections.getByText(/scans only run when you click Scan Now/i),
    ).toBeVisible();
    await expect(
      connections.getByRole("heading", { name: "alpha.mailbox@example.com" }),
    ).toBeVisible();
    await expect(connections.getByText("Gmail read-only")).toBeVisible();

    await connections.getByRole("button", { name: "More" }).click();
    await connections
      .getByRole("menuitem", { name: "Reset local data..." })
      .click();

    const dialog = page.getByRole("dialog", {
      name: "Reset local data for alpha.mailbox@example.com",
    });
    await expect(dialog).toBeVisible();
    await expect(
      dialog.getByText(/This only clears SANE's local data/i),
    ).toBeVisible();
    await expect(
      dialog.getByText(
        /Current ALPHA data model cannot preserve decisions when sources are deleted/i,
      ),
    ).toBeVisible();
    await expect(
      dialog.getByRole("button", { name: "Clear local data" }),
    ).toBeDisabled();

    await dialog.getByRole("button", { name: "Cancel" }).click();
    await expect(dialog).toBeHidden();

    expect(
      mockApi.countRequests("/api/gmail/accounts/2/reset-local-data", "POST"),
    ).toBe(0);
    expect(mockApi.countRequests("/api/gmail/scan", "POST")).toBe(0);
  });

  test("Review evidence and Decisions history stay deterministic and local-only", async ({
    page,
  }) => {
    const mockApi = await installSaneMockApi(page, "mailbox");

    await page.goto("/");

    const review = page.getByRole("main", { name: "Source Review" });
    await expect(review).toBeVisible();
    await expect(
      review.getByRole("heading", { name: "alpha.mailbox@example.com" }),
    ).toBeVisible();
    await expect(review.getByText("Page 1 of 2")).toBeVisible();
    await expect(
      review.getByText(/No external email actions are executed in this ALPHA/i),
    ).toBeVisible();

    const dailyRow = review.getByRole("row", { name: /Daily Deals Dispatch/i });
    await dailyRow.getByRole("button", { name: "Show evidence" }).click();
    await expect(review.getByText("Sender domains")).toBeVisible();
    await expect(review.getByText("No local decision recorded")).toBeVisible();
    await dailyRow.getByRole("button", { name: "Hide evidence" }).click();
    await expect(review.getByText("Sender domains")).toBeHidden();

    await expect(review.getByText("7 queued sources")).toBeVisible();
    await dailyRow.getByRole("button", { name: "Keep Source" }).click();
    await expect(review.getByText("6 queued sources")).toBeVisible();
    await expect(
      review.getByRole("row", { name: /Daily Deals Dispatch/i }),
    ).toHaveCount(0);

    await page.getByRole("button", { name: "Decisions" }).click();
    const decisions = page.getByRole("main", {
      name: "Source Decision History",
    });
    await expect(decisions).toBeVisible();
    await expect(
      decisions.getByRole("heading", { name: "alpha.mailbox@example.com" }),
    ).toBeVisible();
    await expect(decisions.getByText("Daily Deals Dispatch")).toBeVisible();
    await expect(decisions.getByText("Page 1 of 2")).toBeVisible();
    const historyTable = decisions.getByRole("table", {
      name: "Source decision history",
    });
    await expect(historyTable.getByText("Not executed").first()).toBeVisible();
    await expect(historyTable.getByText("Current").first()).toBeVisible();
    await expect(historyTable.getByText("Revision").first()).toBeVisible();

    await decisions.getByRole("button", { name: "Next" }).click();
    await expect(decisions.getByText("Page 2 of 2")).toBeVisible();

    await decisions
      .getByRole("combobox", { name: "Decision page size" })
      .selectOption("10");
    await expect(decisions.getByText("Page 1 of 1")).toBeVisible();

    expect(mockApi.countRequests("/api/gmail/scan", "POST")).toBe(0);
    expect(
      mockApi.countRequests("/api/gmail/accounts/2/reset-local-data", "POST"),
    ).toBe(0);
  });
});
