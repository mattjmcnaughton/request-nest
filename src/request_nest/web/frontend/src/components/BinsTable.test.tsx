import { describe, it, expect, vi, beforeEach } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { BinsTable } from "./BinsTable";
import { renderWithProviders, createTestBin } from "../test";

describe("BinsTable", () => {
  beforeEach(() => {
    // Mock clipboard API
    Object.defineProperty(navigator, "clipboard", {
      value: {
        writeText: vi.fn().mockResolvedValue(undefined),
      },
      writable: true,
      configurable: true,
    });
  });

  describe("empty state", () => {
    it("shows empty message when no bins", () => {
      renderWithProviders(<BinsTable bins={[]} />);

      expect(screen.getByText(/no bins yet/i)).toBeInTheDocument();
    });
  });

  describe("with bins", () => {
    it("displays bin name", () => {
      const bin = createTestBin({ name: "My Webhook" });
      renderWithProviders(<BinsTable bins={[bin]} />);

      // Both mobile and desktop layouts render, so use getAllBy
      const names = screen.getAllByText("My Webhook");
      expect(names.length).toBeGreaterThan(0);
    });

    it("displays 'Unnamed' for bins without name", () => {
      const bin = createTestBin({ name: null });
      renderWithProviders(<BinsTable bins={[bin]} />);

      expect(screen.getAllByText("Unnamed").length).toBeGreaterThan(0);
    });

    it("displays bin ID", () => {
      const bin = createTestBin({ id: "b_test123" });
      renderWithProviders(<BinsTable bins={[bin]} />);

      // Both layouts render the ID
      const ids = screen.getAllByText("b_test123");
      expect(ids.length).toBeGreaterThan(0);
    });

    it("displays ingest URL", () => {
      const bin = createTestBin({ ingest_url: "/b/test123/webhook" });
      renderWithProviders(<BinsTable bins={[bin]} />);

      const urls = screen.getAllByText("/b/test123/webhook");
      expect(urls.length).toBeGreaterThan(0);
    });

    it("displays multiple bins", () => {
      const bins = [
        createTestBin({ id: "b_1", name: "Bin One" }),
        createTestBin({ id: "b_2", name: "Bin Two" }),
        createTestBin({ id: "b_3", name: "Bin Three" }),
      ];
      renderWithProviders(<BinsTable bins={bins} />);

      expect(screen.getAllByText("Bin One").length).toBeGreaterThan(0);
      expect(screen.getAllByText("Bin Two").length).toBeGreaterThan(0);
      expect(screen.getAllByText("Bin Three").length).toBeGreaterThan(0);
    });
  });

  describe("copy button", () => {
    it("has copy buttons for each bin", () => {
      const bin = createTestBin({ ingest_url: "/b/copytest/webhook" });
      renderWithProviders(<BinsTable bins={[bin]} />);

      const copyButtons = screen.getAllByTitle("Copy to clipboard");
      // Both mobile and desktop layouts render
      expect(copyButtons.length).toBeGreaterThan(0);
    });

    it("shows 'Copied!' feedback after clicking", async () => {
      const user = userEvent.setup();
      const bin = createTestBin();
      renderWithProviders(<BinsTable bins={[bin]} />);

      const copyButtons = screen.getAllByTitle("Copy to clipboard");
      await user.click(copyButtons[0]);

      expect(screen.getAllByText("Copied!").length).toBeGreaterThan(0);
    });
  });
});
