import type { Bin, EventSummary, Event } from "../types";

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
   * Fetch a single bin by ID.
   * @throws {ApiError} If the request fails or bin not found (404)
   */
  getBin(binId: string): Promise<Bin>;

  /**
   * Create a new bin.
   * @param name Optional name for the bin
   * @throws {ApiError} If the request fails
   */
  createBin(name: string | null): Promise<Bin>;

  /**
   * List events for a bin.
   * @throws {ApiError} If the request fails
   */
  listEventsForBin(binId: string): Promise<EventSummary[]>;

  /**
   * Fetch a single event by ID.
   * @throws {ApiError} If the request fails or event not found (404)
   */
  getEvent(eventId: string): Promise<Event>;
}
