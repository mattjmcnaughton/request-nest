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
 * Full event detail matching the backend EventDetail DTO.
 */
export interface Event {
  id: string;
  bin_id: string;
  method: string;
  path: string;
  query_params: Record<string, string>;
  headers: Record<string, string>;
  body: string;
  remote_ip: string | null;
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
