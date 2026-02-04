import type { ReactNode } from "react";
import type { BinApiClient } from "../api/client";
import { ApiContext } from "./apiContext";

interface ApiProviderProps {
  client: BinApiClient;
  children: ReactNode;
}

/**
 * Provider component that makes the API client available to all child components.
 */
export function ApiProvider({ client, children }: ApiProviderProps) {
  return <ApiContext.Provider value={client}>{children}</ApiContext.Provider>;
}
