import type { BinApiClient } from "./client";
import type { Bin } from "../types";

/**
 * Generate a random ID similar to the backend's bin ID format.
 */
function generateBinId(): string {
  const chars =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  let result = "";
  for (let i = 0; i < 16; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return `b_${result}`;
}

/**
 * Fake API client for testing.
 *
 * This implementation stores bins in memory, matching the pattern
 * of FakeBinRepository in the backend tests.
 */
export class FakeBinApiClient implements BinApiClient {
  private bins: Map<string, Bin> = new Map();

  /**
   * Clear all stored bins. Call this between tests.
   */
  clear(): void {
    this.bins.clear();
  }

  /**
   * Add a bin directly (for test setup).
   */
  addBin(bin: Bin): void {
    this.bins.set(bin.id, bin);
  }

  /**
   * Get all bins (for test assertions).
   */
  getBins(): Bin[] {
    return Array.from(this.bins.values());
  }

  async listBins(): Promise<Bin[]> {
    return Array.from(this.bins.values());
  }

  async createBin(name: string | null): Promise<Bin> {
    const bin: Bin = {
      id: generateBinId(),
      name,
      ingest_url: `/b/${generateBinId()}`,
      created_at: new Date().toISOString(),
    };
    this.bins.set(bin.id, bin);
    return bin;
  }
}

/**
 * Create a FakeApiClient pre-populated with test bins.
 */
export function createFakeClientWithBins(bins: Bin[]): FakeBinApiClient {
  const client = new FakeBinApiClient();
  for (const bin of bins) {
    client.addBin(bin);
  }
  return client;
}
