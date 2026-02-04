/**
 * Standard API error response format.
 */
export interface ApiErrorResponse {
  error: {
    code: string;
    message: string;
  };
}

/**
 * Custom error class for API errors.
 */
export class ApiError extends Error {
  readonly code: string;
  readonly status: number;

  constructor(code: string, message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.code = code;
    this.status = status;
  }

  static isUnauthorized(error: unknown): boolean {
    return error instanceof ApiError && error.status === 401;
  }
}
