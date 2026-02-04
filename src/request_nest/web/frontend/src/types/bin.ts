/**
 * Bin type matching the backend BinResponse DTO.
 */
export interface Bin {
  id: string;
  name: string | null;
  ingest_url: string;
  created_at: string;
}

/**
 * Response from GET /api/v1/bins
 */
export interface BinListResponse {
  bins: Bin[];
}

/**
 * Request body for POST /api/v1/bins
 */
export interface CreateBinRequest {
  name?: string | null;
}
