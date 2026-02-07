import type { BinApiClient } from "./client";
import type { Bin, Event, EventSummary } from "../types";
import { ApiError } from "../types";

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
 * This implementation stores bins and events in memory, matching the pattern
 * of FakeBinRepository in the backend tests.
 */
export class FakeBinApiClient implements BinApiClient {
  private bins: Map<string, Bin> = new Map();
  private events: Map<string, EventSummary[]> = new Map();
  private eventDetails: Map<string, Event> = new Map();

  /**
   * Clear all stored bins and events. Call this between tests.
   */
  clear(): void {
    this.bins.clear();
    this.events.clear();
    this.eventDetails.clear();
  }

  /**
   * Add a bin directly (for test setup).
   */
  addBin(bin: Bin): void {
    this.bins.set(bin.id, bin);
  }

  /**
   * Add an event to a bin (for test setup).
   */
  addEvent(binId: string, event: EventSummary): void {
    const binEvents = this.events.get(binId) ?? [];
    binEvents.push(event);
    this.events.set(binId, binEvents);
  }

  /**
   * Add multiple events to a bin (for test setup).
   */
  addEvents(binId: string, events: EventSummary[]): void {
    for (const event of events) {
      this.addEvent(binId, event);
    }
  }

  /**
   * Add a full event detail (for test setup).
   */
  addEventDetail(event: Event): void {
    this.eventDetails.set(event.id, event);
  }

  /**
   * Get all bins (for test assertions).
   */
  getBins(): Bin[] {
    return Array.from(this.bins.values());
  }

  /**
   * Get events for a bin (for test assertions).
   */
  getEvents(binId: string): EventSummary[] {
    return this.events.get(binId) ?? [];
  }

  async listBins(): Promise<Bin[]> {
    return Array.from(this.bins.values());
  }

  async getBin(binId: string): Promise<Bin> {
    const bin = this.bins.get(binId);
    if (!bin) {
      throw new ApiError("NOT_FOUND", `Bin ${binId} not found`, 404);
    }
    return bin;
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

  async listEventsForBin(binId: string): Promise<EventSummary[]> {
    return this.events.get(binId) ?? [];
  }

  async getEvent(eventId: string): Promise<Event> {
    const event = this.eventDetails.get(eventId);
    if (!event) {
      throw new ApiError("NOT_FOUND", `Event ${eventId} not found`, 404);
    }
    return event;
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

/**
 * Create a FakeApiClient pre-populated with a bin and its events.
 */
export function createFakeClientWithBinAndEvents(
  bin: Bin,
  events: EventSummary[],
): FakeBinApiClient {
  const client = new FakeBinApiClient();
  client.addBin(bin);
  client.addEvents(bin.id, events);
  return client;
}

/**
 * Create a FakeApiClient pre-populated with an event detail and its parent bin.
 */
export function createFakeClientWithEventDetail(
  bin: Bin,
  event: Event,
): FakeBinApiClient {
  const client = new FakeBinApiClient();
  client.addBin(bin);
  client.addEventDetail(event);
  return client;
}
