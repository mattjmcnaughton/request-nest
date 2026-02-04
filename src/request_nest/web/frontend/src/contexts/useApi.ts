import { useContext } from "react";
import type { BinApiClient } from "../api/client";
import { ApiContext } from "./apiContext";

/**
 * Hook to access the API client from any component.
 * Must be used within an ApiProvider.
 */
export function useApi(): BinApiClient {
  const client = useContext(ApiContext);
  if (!client) {
    throw new Error("useApi must be used within an ApiProvider");
  }
  return client;
}
