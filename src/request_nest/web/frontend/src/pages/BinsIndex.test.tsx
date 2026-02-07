import { describe, it, expect, vi, beforeEach } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { BinsIndex } from "./BinsIndex";
import { renderWithProviders, createTestBin } from "../test";
import { FakeBinApiClient, createFakeClientWithBins } from "../api";
import { setToken, clearToken } from "../utils";

describe("BinsIndex", () => {
  beforeEach(() => {
    // Start each test with a valid token
    setToken("test-token");
    // Mock clipboard API using vi.stubGlobal
    const clipboardMock = {
      writeText: vi.fn().mockResolvedValue(undefined),
    };
    vi.stubGlobal("navigator", {
      ...navigator,
      clipboard: clipboardMock,
    });
  });

  describe("authentication", () => {
    it("shows auth prompt when no token is stored", () => {
      clearToken();
      renderWithProviders(<BinsIndex />);

      expect(screen.getByText("auth required")).toBeInTheDocument();
    });

    it("fetches bins after authentication", async () => {
      clearToken();
      const user = userEvent.setup();
      const bins = [createTestBin({ name: "Test Bin" })];
      const apiClient = createFakeClientWithBins(bins);

      renderWithProviders(<BinsIndex />, { apiClient });

      // Enter token
      await user.type(screen.getByLabelText(/token/i), "my-token");
      await user.click(screen.getByRole("button", { name: /authenticate/i }));

      // Should now show bins (both mobile and desktop render, use getAllBy)
      await waitFor(() => {
        expect(screen.getAllByText("Test Bin").length).toBeGreaterThan(0);
      });
    });
  });

  describe("loading state", () => {
    it("shows loading spinner while fetching", () => {
      const slowClient = {
        listBins: vi
          .fn()
          .mockImplementation(
            () => new Promise((resolve) => setTimeout(() => resolve([]), 500)),
          ),
        getBin: vi.fn(),
        createBin: vi.fn(),
        listEventsForBin: vi.fn(),
        getEvent: vi.fn(),
      };

      renderWithProviders(<BinsIndex />, { apiClient: slowClient });

      // Check for loading spinner (the animate-spin class)
      const spinner = document.querySelector(".animate-spin");
      expect(spinner).toBeInTheDocument();
    });
  });

  describe("bins display", () => {
    it("displays bins from API", async () => {
      const bins = [
        createTestBin({ name: "Webhook 1" }),
        createTestBin({ name: "Webhook 2" }),
      ];
      const apiClient = createFakeClientWithBins(bins);

      renderWithProviders(<BinsIndex />, { apiClient });

      await waitFor(() => {
        expect(screen.getAllByText("Webhook 1").length).toBeGreaterThan(0);
        expect(screen.getAllByText("Webhook 2").length).toBeGreaterThan(0);
      });
    });

    it("shows empty state when no bins exist", async () => {
      const apiClient = new FakeBinApiClient();

      renderWithProviders(<BinsIndex />, { apiClient });

      await waitFor(() => {
        expect(screen.getByText(/no bins yet/i)).toBeInTheDocument();
      });
    });
  });

  describe("create bin", () => {
    it("opens create modal when button is clicked", async () => {
      const user = userEvent.setup();
      const apiClient = new FakeBinApiClient();

      renderWithProviders(<BinsIndex />, { apiClient });

      await waitFor(() => {
        expect(
          screen.getByRole("button", { name: /new bin/i }),
        ).toBeInTheDocument();
      });

      await user.click(screen.getByRole("button", { name: /new bin/i }));

      expect(screen.getByText("new bin", { selector: "h2" })).toBeInTheDocument();
    });

    it("refreshes list after creating a bin", async () => {
      const user = userEvent.setup();
      const apiClient = new FakeBinApiClient();

      renderWithProviders(<BinsIndex />, { apiClient });

      // Wait for initial load
      await waitFor(() => {
        expect(screen.getByText(/no bins yet/i)).toBeInTheDocument();
      });

      // Open modal and create bin
      await user.click(screen.getByRole("button", { name: /new bin/i }));
      await user.type(screen.getByLabelText(/name/i), "New Webhook");

      await user.click(screen.getByRole("button", { name: /^create$/i }));

      // Should show the new bin (both layouts render)
      await waitFor(() => {
        expect(screen.getAllByText("New Webhook").length).toBeGreaterThan(0);
      });
    });
  });

  describe("header", () => {
    it("displays page title", async () => {
      const apiClient = new FakeBinApiClient();
      renderWithProviders(<BinsIndex />, { apiClient });

      await waitFor(() => {
        expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(
          "$ bins",
        );
      });
    });

    it("displays subtitle", async () => {
      const apiClient = new FakeBinApiClient();
      renderWithProviders(<BinsIndex />, { apiClient });

      await waitFor(() => {
        expect(
          screen.getByText(/webhook inbox for capturing http requests/i),
        ).toBeInTheDocument();
      });
    });
  });
});
