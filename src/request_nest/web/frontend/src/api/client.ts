import type { Bin } from "../types";

/**
 * API client interface for bin operations.
 *
 * This interface defines the contract that both the real API client
 * and fake client (for testing) must implement.
 */
export interface BinApiClient {
  /**
   * Fetch all bins.
   * @throws {ApiError} If the request fails
   */
  listBins(): Promise<Bin[]>;

  /**
   * Create a new bin.
   * @param name Optional name for the bin
   * @throws {ApiError} If the request fails
   */
  createBin(name: string | null): Promise<Bin>;
}
