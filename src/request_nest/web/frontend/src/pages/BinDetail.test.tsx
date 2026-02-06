import { describe, it, expect, vi, beforeEach } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Routes, Route } from "react-router";
import { BinDetail } from "./BinDetail";
import { renderWithProviders, createTestBin, createTestEvent } from "../test";
import {
  FakeBinApiClient,
  createFakeClientWithBinAndEvents,
} from "../api";
import { setToken, clearToken } from "../utils";
import { ApiError } from "../types";

const TEST_BIN_ID = "b_test123";

function renderBinDetail(apiClient: FakeBinApiClient) {
  return renderWithProviders(
    <Routes>
      <Route path="/bins/:binId" element={<BinDetail />} />
    </Routes>,
    {
      apiClient,
      initialEntries: [`/bins/${TEST_BIN_ID}`],
    },
  );
}

describe("BinDetail", () => {
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

      renderBinDetail(apiClient);

      await waitFor(() => {
        expect(screen.getByText("Authentication Required")).toBeInTheDocument();
      });
    });
  });

  describe("loading state", () => {
    it("shows loading spinner while fetching", () => {
      const slowClient = new FakeBinApiClient();
      // Override getBin to be slow
      slowClient.getBin = vi.fn().mockImplementation(
        () =>
          new Promise((resolve) =>
            setTimeout(() => resolve(createTestBin({ id: TEST_BIN_ID })), 500),
          ),
      );
      slowClient.listEventsForBin = vi.fn().mockImplementation(
        () =>
          new Promise((resolve) => setTimeout(() => resolve([]), 500)),
      );

      renderBinDetail(slowClient);

      const spinner = document.querySelector(".animate-spin");
      expect(spinner).toBeInTheDocument();
    });
  });

  describe("bin display", () => {
    it("displays bin name", async () => {
      const bin = createTestBin({ id: TEST_BIN_ID, name: "My Webhook" });
      const apiClient = createFakeClientWithBinAndEvents(bin, []);

      renderBinDetail(apiClient);

      await waitFor(() => {
        expect(
          screen.getByRole("heading", { name: "My Webhook" }),
        ).toBeInTheDocument();
      });
    });

    it("displays 'Unnamed Bin' for bins without name", async () => {
      const bin = createTestBin({ id: TEST_BIN_ID, name: null });
      const apiClient = createFakeClientWithBinAndEvents(bin, []);

      renderBinDetail(apiClient);

      await waitFor(() => {
        expect(screen.getByText("Unnamed Bin")).toBeInTheDocument();
      });
    });

    it("displays bin ID", async () => {
      const bin = createTestBin({ id: TEST_BIN_ID });
      const apiClient = createFakeClientWithBinAndEvents(bin, []);

      renderBinDetail(apiClient);

      await waitFor(() => {
        expect(screen.getByText(TEST_BIN_ID)).toBeInTheDocument();
      });
    });

    it("displays ingest URL", async () => {
      const bin = createTestBin({
        id: TEST_BIN_ID,
        ingest_url: "/b/test123/webhook",
      });
      const apiClient = createFakeClientWithBinAndEvents(bin, []);

      renderBinDetail(apiClient);

      await waitFor(() => {
        expect(screen.getByText("/b/test123/webhook")).toBeInTheDocument();
      });
    });
  });

  describe("events display", () => {
    it("displays events in table", async () => {
      const bin = createTestBin({ id: TEST_BIN_ID });
      const events = [
        createTestEvent({ id: "e_1", method: "POST", path: "/api/webhook" }),
        createTestEvent({ id: "e_2", method: "GET", path: "/health" }),
      ];
      const apiClient = createFakeClientWithBinAndEvents(bin, events);

      renderBinDetail(apiClient);

      await waitFor(() => {
        // Check method badges (both mobile and desktop render)
        expect(screen.getAllByText("POST").length).toBeGreaterThan(0);
        expect(screen.getAllByText("GET").length).toBeGreaterThan(0);
        // Check paths
        expect(screen.getAllByText("/api/webhook").length).toBeGreaterThan(0);
        expect(screen.getAllByText("/health").length).toBeGreaterThan(0);
      });
    });

    it("shows empty state when no events", async () => {
      const bin = createTestBin({ id: TEST_BIN_ID });
      const apiClient = createFakeClientWithBinAndEvents(bin, []);

      renderBinDetail(apiClient);

      await waitFor(() => {
        expect(screen.getByText(/no events captured yet/i)).toBeInTheDocument();
      });
    });

    it("displays event size", async () => {
      const bin = createTestBin({ id: TEST_BIN_ID });
      const events = [createTestEvent({ size_bytes: 256 })];
      const apiClient = createFakeClientWithBinAndEvents(bin, events);

      renderBinDetail(apiClient);

      await waitFor(() => {
        expect(screen.getAllByText("256 B").length).toBeGreaterThan(0);
      });
    });
  });

  describe("navigation", () => {
    it("has back link to bins list", async () => {
      const bin = createTestBin({ id: TEST_BIN_ID });
      const apiClient = createFakeClientWithBinAndEvents(bin, []);

      renderBinDetail(apiClient);

      await waitFor(() => {
        const backLink = screen.getByRole("link", { name: /back to bins/i });
        expect(backLink).toHaveAttribute("href", "/");
      });
    });
  });

  describe("copy button", () => {
    it("shows 'Copied!' feedback after clicking", async () => {
      const user = userEvent.setup();
      const bin = createTestBin({ id: TEST_BIN_ID });
      const apiClient = createFakeClientWithBinAndEvents(bin, []);

      renderBinDetail(apiClient);

      await waitFor(() => {
        expect(screen.getByTitle("Copy to clipboard")).toBeInTheDocument();
      });

      const copyButton = screen.getByTitle("Copy to clipboard");
      await user.click(copyButton);

      expect(screen.getByText("Copied!")).toBeInTheDocument();
    });
  });

  describe("404 state", () => {
    it("shows not found message when bin does not exist", async () => {
      const apiClient = new FakeBinApiClient();
      // No bin added, so getBin will throw 404

      renderBinDetail(apiClient);

      await waitFor(() => {
        expect(screen.getByText("Bin Not Found")).toBeInTheDocument();
        expect(
          screen.getByText(/does not exist or has been deleted/i),
        ).toBeInTheDocument();
      });
    });

    it("has link back to bins list in 404 state", async () => {
      const apiClient = new FakeBinApiClient();

      renderBinDetail(apiClient);

      await waitFor(() => {
        const backLink = screen.getByRole("link", { name: /back to bins list/i });
        expect(backLink).toHaveAttribute("href", "/");
      });
    });
  });

  describe("error state", () => {
    it("shows error message on API failure", async () => {
      const apiClient = new FakeBinApiClient();
      apiClient.getBin = vi
        .fn()
        .mockRejectedValue(new ApiError("SERVER_ERROR", "Internal error", 500));

      renderBinDetail(apiClient);

      await waitFor(() => {
        expect(screen.getByText("Internal error")).toBeInTheDocument();
      });
    });

    it("has retry button on error", async () => {
      const apiClient = new FakeBinApiClient();
      apiClient.getBin = vi
        .fn()
        .mockRejectedValue(new ApiError("SERVER_ERROR", "Internal error", 500));

      renderBinDetail(apiClient);

      await waitFor(() => {
        expect(
          screen.getByRole("button", { name: /try again/i }),
        ).toBeInTheDocument();
      });
    });
  });
});
