import { render, type RenderOptions } from "@testing-library/react";
import type { ReactElement, ReactNode } from "react";
import { ApiProvider } from "../contexts";
import { FakeBinApiClient } from "../api";
import type { BinApiClient } from "../api";

interface WrapperProps {
  children: ReactNode;
}

interface CustomRenderOptions extends Omit<RenderOptions, "wrapper"> {
  apiClient?: BinApiClient;
}

/**
 * Custom render function that wraps components with ApiProvider.
 * Uses FakeBinApiClient by default for isolated testing.
 */
export function renderWithProviders(
  ui: ReactElement,
  { apiClient = new FakeBinApiClient(), ...options }: CustomRenderOptions = {},
) {
  function Wrapper({ children }: WrapperProps) {
    return <ApiProvider client={apiClient}>{children}</ApiProvider>;
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
