const TOKEN_KEY = "request_nest_admin_token";

/**
 * Get the stored admin token from localStorage.
 */
export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

/**
 * Store the admin token in localStorage.
 */
export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

/**
 * Remove the admin token from localStorage.
 */
export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

/**
 * Check if a token is currently stored.
 */
export function hasToken(): boolean {
  return getToken() !== null;
}
