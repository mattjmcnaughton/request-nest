import { describe, it, expect, vi, beforeEach } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Routes, Route } from "react-router";
import { EventDetail } from "./EventDetail";
import {
  renderWithProviders,
  createTestBin,
  createTestEventDetail,
} from "../test";
import {
  FakeBinApiClient,
  createFakeClientWithEventDetail,
} from "../api";
import { setToken, clearToken } from "../utils";
import { ApiError } from "../types";

const TEST_EVENT_ID = "e_test123";
const TEST_BIN_ID = "b_test123";

function renderEventDetail(apiClient: FakeBinApiClient) {
  return renderWithProviders(
    <Routes>
      <Route path="/events/:eventId" element={<EventDetail />} />
    </Routes>,
    {
      apiClient,
      initialEntries: [`/events/${TEST_EVENT_ID}`],
    },
  );
}

describe("EventDetail", () => {
  beforeEach(() => {
    setToken("test-token");
    Object.defineProperty(navigator, "clipboard", {
      value: {
        writeText: vi.fn().mockResolvedValue(undefined),
      },
      writable: true,
      configurable: true,
    });
  });

  describe("authentication", () => {
    it("shows auth prompt when no token is stored", async () => {
      clearToken();
      const apiClient = new FakeBinApiClient();

      renderEventDetail(apiClient);

      await waitFor(() => {
        expect(screen.getByText("auth required")).toBeInTheDocument();
      });
    });
  });

  describe("loading state", () => {
    it("shows loading spinner while fetching", () => {
      const slowClient = new FakeBinApiClient();
      slowClient.getEvent = vi.fn().mockImplementation(
        () =>
          new Promise((resolve) =>
            setTimeout(
              () =>
                resolve(
                  createTestEventDetail({ id: TEST_EVENT_ID }),
                ),
              500,
            ),
          ),
      );

      renderEventDetail(slowClient);

      const spinner = document.querySelector(".animate-spin");
      expect(spinner).toBeInTheDocument();
    });
  });

  describe("404 state", () => {
    it("shows not found message when event does not exist", async () => {
      const apiClient = new FakeBinApiClient();

      renderEventDetail(apiClient);

      await waitFor(() => {
        expect(screen.getByText("event not found")).toBeInTheDocument();
        expect(
          screen.getByText(/does not exist or has been deleted/i),
        ).toBeInTheDocument();
      });
    });

    it("has link back to bins list in 404 state", async () => {
      const apiClient = new FakeBinApiClient();

      renderEventDetail(apiClient);

      await waitFor(() => {
        const backLink = screen.getByRole("link", {
          name: /back to bins/i,
        });
        expect(backLink).toHaveAttribute("href", "/");
      });
    });
  });

  describe("error state", () => {
    it("shows error message on API failure", async () => {
      const apiClient = new FakeBinApiClient();
      apiClient.getEvent = vi
        .fn()
        .mockRejectedValue(
          new ApiError("SERVER_ERROR", "Internal error", 500),
        );

      renderEventDetail(apiClient);

      await waitFor(() => {
        expect(screen.getByText("Internal error")).toBeInTheDocument();
      });
    });

    it("has retry button on error", async () => {
      const apiClient = new FakeBinApiClient();
      apiClient.getEvent = vi
        .fn()
        .mockRejectedValue(
          new ApiError("SERVER_ERROR", "Internal error", 500),
        );

      renderEventDetail(apiClient);

      await waitFor(() => {
        expect(
          screen.getByRole("button", { name: /retry/i }),
        ).toBeInTheDocument();
      });
    });
  });

  describe("event display", () => {
    it("displays HTTP method and path", async () => {
      const bin = createTestBin({ id: TEST_BIN_ID });
      const event = createTestEventDetail({
        id: TEST_EVENT_ID,
        bin_id: TEST_BIN_ID,
        method: "POST",
        path: "/api/webhook",
      });
      const apiClient = createFakeClientWithEventDetail(bin, event);

      renderEventDetail(apiClient);

      await waitFor(() => {
        expect(screen.getByText("POST")).toBeInTheDocument();
        expect(screen.getByText("/api/webhook")).toBeInTheDocument();
      });
    });

    it("displays event ID", async () => {
      const bin = createTestBin({ id: TEST_BIN_ID });
      const event = createTestEventDetail({
        id: TEST_EVENT_ID,
        bin_id: TEST_BIN_ID,
      });
      const apiClient = createFakeClientWithEventDetail(bin, event);

      renderEventDetail(apiClient);

      await waitFor(() => {
        expect(screen.getAllByText(TEST_EVENT_ID).length).toBeGreaterThan(0);
      });
    });

    it("displays remote IP", async () => {
      const bin = createTestBin({ id: TEST_BIN_ID });
      const event = createTestEventDetail({
        id: TEST_EVENT_ID,
        bin_id: TEST_BIN_ID,
        remote_ip: "192.168.1.1",
      });
      const apiClient = createFakeClientWithEventDetail(bin, event);

      renderEventDetail(apiClient);

      await waitFor(() => {
        expect(screen.getByText("192.168.1.1")).toBeInTheDocument();
      });
    });

    it("displays headers in key-value table", async () => {
      const bin = createTestBin({ id: TEST_BIN_ID });
      const event = createTestEventDetail({
        id: TEST_EVENT_ID,
        bin_id: TEST_BIN_ID,
        headers: {
          "content-type": "application/json",
          "x-custom-header": "test-value",
        },
      });
      const apiClient = createFakeClientWithEventDetail(bin, event);

      renderEventDetail(apiClient);

      await waitFor(() => {
        expect(screen.getByText("content-type")).toBeInTheDocument();
        expect(screen.getByText("application/json")).toBeInTheDocument();
        expect(screen.getByText("x-custom-header")).toBeInTheDocument();
        expect(screen.getByText("test-value")).toBeInTheDocument();
      });
    });

    it("displays query parameters when present", async () => {
      const bin = createTestBin({ id: TEST_BIN_ID });
      const event = createTestEventDetail({
        id: TEST_EVENT_ID,
        bin_id: TEST_BIN_ID,
        query_params: { foo: "bar", baz: "qux" },
      });
      const apiClient = createFakeClientWithEventDetail(bin, event);

      renderEventDetail(apiClient);

      await waitFor(() => {
        expect(screen.getByText("query_params")).toBeInTheDocument();
        expect(screen.getByText("foo")).toBeInTheDocument();
        expect(screen.getByText("bar")).toBeInTheDocument();
        expect(screen.getByText("baz")).toBeInTheDocument();
        expect(screen.getByText("qux")).toBeInTheDocument();
      });
    });

    it("hides query parameters section when empty", async () => {
      const bin = createTestBin({ id: TEST_BIN_ID });
      const event = createTestEventDetail({
        id: TEST_EVENT_ID,
        bin_id: TEST_BIN_ID,
        query_params: {},
      });
      const apiClient = createFakeClientWithEventDetail(bin, event);

      renderEventDetail(apiClient);

      await waitFor(() => {
        expect(screen.getByText("headers")).toBeInTheDocument();
      });

      expect(screen.queryByText("query_params")).not.toBeInTheDocument();
    });

    it("pretty-prints JSON body", async () => {
      const bin = createTestBin({ id: TEST_BIN_ID });
      const event = createTestEventDetail({
        id: TEST_EVENT_ID,
        bin_id: TEST_BIN_ID,
        body: '{"name":"test","count":42}',
      });
      const apiClient = createFakeClientWithEventDetail(bin, event);

      renderEventDetail(apiClient);

      await waitFor(() => {
        const pre = document.querySelector("pre");
        expect(pre).toBeInTheDocument();
        expect(pre?.textContent).toContain('"name": "test"');
        expect(pre?.textContent).toContain('"count": 42');
      });
    });

    it("displays non-JSON body as raw text", async () => {
      const bin = createTestBin({ id: TEST_BIN_ID });
      const event = createTestEventDetail({
        id: TEST_EVENT_ID,
        bin_id: TEST_BIN_ID,
        body: "plain text body content",
      });
      const apiClient = createFakeClientWithEventDetail(bin, event);

      renderEventDetail(apiClient);

      await waitFor(() => {
        expect(screen.getByText("plain text body content")).toBeInTheDocument();
      });
    });

    it("hides body section when body is empty", async () => {
      const bin = createTestBin({ id: TEST_BIN_ID });
      const event = createTestEventDetail({
        id: TEST_EVENT_ID,
        bin_id: TEST_BIN_ID,
        body: "",
      });
      const apiClient = createFakeClientWithEventDetail(bin, event);

      renderEventDetail(apiClient);

      await waitFor(() => {
        expect(screen.getByText("headers")).toBeInTheDocument();
      });

      expect(screen.queryByText("body")).not.toBeInTheDocument();
    });

    it("shows JSON label for JSON bodies", async () => {
      const bin = createTestBin({ id: TEST_BIN_ID });
      const event = createTestEventDetail({
        id: TEST_EVENT_ID,
        bin_id: TEST_BIN_ID,
        body: '{"key": "value"}',
      });
      const apiClient = createFakeClientWithEventDetail(bin, event);

      renderEventDetail(apiClient);

      await waitFor(() => {
        expect(screen.getByText("(json)")).toBeInTheDocument();
      });
    });
  });

  describe("copy buttons", () => {
    it("copies headers when copy button is clicked", async () => {
      const user = userEvent.setup();
      const bin = createTestBin({ id: TEST_BIN_ID });
      const event = createTestEventDetail({
        id: TEST_EVENT_ID,
        bin_id: TEST_BIN_ID,
        headers: { "content-type": "application/json" },
        body: "",
      });
      const apiClient = createFakeClientWithEventDetail(bin, event);

      renderEventDetail(apiClient);

      await waitFor(() => {
        expect(screen.getByTitle("Copy headers")).toBeInTheDocument();
      });

      const copyButton = screen.getByTitle("Copy headers");
      await user.click(copyButton);

      await waitFor(() => {
        expect(screen.getByText("copied")).toBeInTheDocument();
      });
    });

    it("copies body when copy button is clicked", async () => {
      const user = userEvent.setup();
      const bin = createTestBin({ id: TEST_BIN_ID });
      const event = createTestEventDetail({
        id: TEST_EVENT_ID,
        bin_id: TEST_BIN_ID,
        body: '{"key": "value"}',
      });
      const apiClient = createFakeClientWithEventDetail(bin, event);

      renderEventDetail(apiClient);

      await waitFor(() => {
        expect(screen.getByTitle("Copy body")).toBeInTheDocument();
      });

      const copyButton = screen.getByTitle("Copy body");
      await user.click(copyButton);

      await waitFor(() => {
        expect(screen.getAllByText("copied").length).toBeGreaterThan(0);
      });
    });

    it("shows 'Copied!' feedback after clicking copy", async () => {
      const user = userEvent.setup();
      const bin = createTestBin({ id: TEST_BIN_ID });
      const event = createTestEventDetail({
        id: TEST_EVENT_ID,
        bin_id: TEST_BIN_ID,
        headers: { "content-type": "application/json" },
        body: "",
      });
      const apiClient = createFakeClientWithEventDetail(bin, event);

      renderEventDetail(apiClient);

      await waitFor(() => {
        expect(screen.getByTitle("Copy headers")).toBeInTheDocument();
      });

      const copyButton = screen.getByTitle("Copy headers");
      await user.click(copyButton);

      expect(screen.getByText("copied")).toBeInTheDocument();
    });
  });

  describe("breadcrumb navigation", () => {
    it("renders breadcrumb with bin name link", async () => {
      const bin = createTestBin({
        id: TEST_BIN_ID,
        name: "My Webhook Bin",
      });
      const event = createTestEventDetail({
        id: TEST_EVENT_ID,
        bin_id: TEST_BIN_ID,
      });
      const apiClient = createFakeClientWithEventDetail(bin, event);

      renderEventDetail(apiClient);

      await waitFor(() => {
        const binsLink = screen.getByRole("link", { name: "bins" });
        expect(binsLink).toHaveAttribute("href", "/");

        const binLink = screen.getByRole("link", {
          name: "My Webhook Bin",
        });
        expect(binLink).toHaveAttribute("href", `/bins/${TEST_BIN_ID}`);
      });
    });

    it("falls back to bin ID in breadcrumb when bin fetch fails", async () => {
      const apiClient = new FakeBinApiClient();
      const event = createTestEventDetail({
        id: TEST_EVENT_ID,
        bin_id: TEST_BIN_ID,
      });
      apiClient.addEventDetail(event);
      // No bin added, so getBin will throw 404

      renderEventDetail(apiClient);

      await waitFor(() => {
        const binLink = screen.getByRole("link", {
          name: TEST_BIN_ID,
        });
        expect(binLink).toHaveAttribute("href", `/bins/${TEST_BIN_ID}`);
      });
    });

    it("displays event ID in breadcrumb", async () => {
      const bin = createTestBin({ id: TEST_BIN_ID });
      const event = createTestEventDetail({
        id: TEST_EVENT_ID,
        bin_id: TEST_BIN_ID,
      });
      const apiClient = createFakeClientWithEventDetail(bin, event);

      renderEventDetail(apiClient);

      await waitFor(() => {
        expect(screen.getAllByText(TEST_EVENT_ID).length).toBeGreaterThan(0);
      });
    });
  });
});
