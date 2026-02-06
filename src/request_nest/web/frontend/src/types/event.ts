/**
 * Summary of an event captured in a bin.
 * Mirrors EventSummary from backend DTOs.
 */
export interface EventSummary {
  id: string;
  method: string;
  path: string;
  size_bytes: number;
  created_at: string;
}

/**
 * Response containing a list of events.
 * Mirrors EventListResponse from backend DTOs.
 */
export interface EventListResponse {
  events: EventSummary[];
}
