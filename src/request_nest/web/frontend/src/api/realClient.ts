import type { BinApiClient } from "./client";
import type {
  Bin,
  BinListResponse,
  EventSummary,
  EventListResponse,
  ApiErrorResponse,
} from "../types";
import { ApiError } from "../types";
import { getToken } from "../utils/auth";

/**
 * Real API client that makes HTTP requests to the backend.
 */
export class RealBinApiClient implements BinApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = "/api/v1") {
    this.baseUrl = baseUrl;
  }

  async listBins(): Promise<Bin[]> {
    const response = await this.fetch("/bins");
    const data: BinListResponse = await response.json();
    return data.bins;
  }

  async getBin(binId: string): Promise<Bin> {
    const response = await this.fetch(`/bins/${binId}`);
    return response.json();
  }

  async createBin(name: string | null): Promise<Bin> {
    const response = await this.fetch("/bins", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ name }),
    });
    return response.json();
  }

  async listEventsForBin(binId: string): Promise<EventSummary[]> {
    const response = await this.fetch(`/bins/${binId}/events`);
    const data: EventListResponse = await response.json();
    return data.events;
  }

  private async fetch(
    path: string,
    options: RequestInit = {},
  ): Promise<Response> {
    const token = getToken();

    const headers: HeadersInit = {
      ...options.headers,
    };

    if (token) {
      (headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(`${this.baseUrl}${path}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      let errorData: ApiErrorResponse | null = null;
      try {
        errorData = await response.json();
      } catch {
        // Response may not be JSON
      }

      const code = errorData?.error?.code ?? "UNKNOWN_ERROR";
      const message =
        errorData?.error?.message ??
        `Request failed with status ${response.status}`;

      throw new ApiError(code, message, response.status);
    }

    return response;
  }
}
