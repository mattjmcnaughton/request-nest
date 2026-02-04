import { describe, it, expect, vi, beforeEach } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { CreateBinModal } from "./CreateBinModal";
import { renderWithProviders, createTestBin } from "../test";
import { FakeBinApiClient } from "../api";

describe("CreateBinModal", () => {
  let apiClient: FakeBinApiClient;
  let onClose: () => void;
  let onCreated: () => void;

  beforeEach(() => {
    apiClient = new FakeBinApiClient();
    onClose = vi.fn();
    onCreated = vi.fn();
  });

  it("does not render when isOpen is false", () => {
    renderWithProviders(
      <CreateBinModal isOpen={false} onClose={onClose} onCreated={onCreated} />,
      { apiClient },
    );

    expect(screen.queryByText("Create New Bin")).not.toBeInTheDocument();
  });

  it("renders modal when isOpen is true", () => {
    renderWithProviders(
      <CreateBinModal isOpen={true} onClose={onClose} onCreated={onCreated} />,
      { apiClient },
    );

    expect(screen.getByText("Create New Bin")).toBeInTheDocument();
    expect(screen.getByLabelText(/name/i)).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /create bin/i }),
    ).toBeInTheDocument();
  });

  it("creates bin with name when form is submitted", async () => {
    const user = userEvent.setup();
    renderWithProviders(
      <CreateBinModal isOpen={true} onClose={onClose} onCreated={onCreated} />,
      { apiClient },
    );

    await user.type(screen.getByLabelText(/name/i), "My Webhook");
    await user.click(screen.getByRole("button", { name: /create bin/i }));

    await waitFor(() => {
      expect(onCreated).toHaveBeenCalledTimes(1);
    });

    const bins = apiClient.getBins();
    expect(bins).toHaveLength(1);
    expect(bins[0].name).toBe("My Webhook");
  });

  it("creates bin with null name when name is empty", async () => {
    const user = userEvent.setup();
    renderWithProviders(
      <CreateBinModal isOpen={true} onClose={onClose} onCreated={onCreated} />,
      { apiClient },
    );

    await user.click(screen.getByRole("button", { name: /create bin/i }));

    await waitFor(() => {
      expect(onCreated).toHaveBeenCalledTimes(1);
    });

    const bins = apiClient.getBins();
    expect(bins).toHaveLength(1);
    expect(bins[0].name).toBeNull();
  });

  it("calls onClose after successful creation", async () => {
    const user = userEvent.setup();
    renderWithProviders(
      <CreateBinModal isOpen={true} onClose={onClose} onCreated={onCreated} />,
      { apiClient },
    );

    await user.click(screen.getByRole("button", { name: /create bin/i }));

    await waitFor(() => {
      expect(onClose).toHaveBeenCalledTimes(1);
    });
  });

  it("calls onClose when cancel button is clicked", async () => {
    const user = userEvent.setup();
    renderWithProviders(
      <CreateBinModal isOpen={true} onClose={onClose} onCreated={onCreated} />,
      { apiClient },
    );

    await user.click(screen.getByRole("button", { name: /cancel/i }));

    expect(onClose).toHaveBeenCalledTimes(1);
    expect(onCreated).not.toHaveBeenCalled();
  });

  it("shows loading state while creating", async () => {
    const user = userEvent.setup();
    // Make createBin take some time
    const slowClient = {
      listBins: apiClient.listBins.bind(apiClient),
      createBin: vi
        .fn()
        .mockImplementation(
          () =>
            new Promise((resolve) =>
              setTimeout(() => resolve(createTestBin()), 100),
            ),
        ),
    };

    renderWithProviders(
      <CreateBinModal isOpen={true} onClose={onClose} onCreated={onCreated} />,
      { apiClient: slowClient },
    );

    await user.click(screen.getByRole("button", { name: /create bin/i }));

    expect(screen.getByText(/creating/i)).toBeInTheDocument();
  });
});
