import { render, type RenderOptions } from "@testing-library/react";
import type { ReactElement, ReactNode } from "react";
import { MemoryRouter } from "react-router";
import { ApiProvider } from "../contexts";
import { FakeBinApiClient } from "../api";
import type { BinApiClient } from "../api";

interface WrapperProps {
  children: ReactNode;
}

interface CustomRenderOptions extends Omit<RenderOptions, "wrapper"> {
  apiClient?: BinApiClient;
  initialEntries?: string[];
}

/**
 * Custom render function that wraps components with ApiProvider and MemoryRouter.
 * Uses FakeBinApiClient by default for isolated testing.
 */
export function renderWithProviders(
  ui: ReactElement,
  {
    apiClient = new FakeBinApiClient(),
    initialEntries = ["/"],
    ...options
  }: CustomRenderOptions = {},
) {
  function Wrapper({ children }: WrapperProps) {
    return (
      <MemoryRouter initialEntries={initialEntries}>
        <ApiProvider client={apiClient}>{children}</ApiProvider>
      </MemoryRouter>
    );
  }

  return {
    ...render(ui, { wrapper: Wrapper, ...options }),
    apiClient,
  };
}

/**
 * Create a test bin with default values.
 */
export function createTestBin(
  overrides: Partial<import("../types").Bin> = {},
): import("../types").Bin {
  const id = overrides.id ?? `b_test${Math.random().toString(36).slice(2, 10)}`;
  return {
    id,
    name: overrides.name ?? "Test Bin",
    ingest_url: overrides.ingest_url ?? `/b/${id}/webhook`,
    created_at: overrides.created_at ?? new Date().toISOString(),
    ...overrides,
  };
}

/**
 * Create a test event with default values.
 */
export function createTestEvent(
  overrides: Partial<import("../types").EventSummary> = {},
): import("../types").EventSummary {
  const id =
    overrides.id ?? `e_test${Math.random().toString(36).slice(2, 10)}`;
  return {
    id,
    method: overrides.method ?? "POST",
    path: overrides.path ?? "/webhook",
    size_bytes: overrides.size_bytes ?? 128,
    created_at: overrides.created_at ?? new Date().toISOString(),
    ...overrides,
  };
}
