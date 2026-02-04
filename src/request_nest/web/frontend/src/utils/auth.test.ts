import { describe, it, expect } from "vitest";
import { getToken, setToken, clearToken, hasToken } from "./auth";

describe("auth utilities", () => {
  describe("getToken", () => {
    it("returns null when no token is stored", () => {
      expect(getToken()).toBeNull();
    });

    it("returns stored token", () => {
      localStorage.setItem("request_nest_admin_token", "test-token");
      expect(getToken()).toBe("test-token");
    });
  });

  describe("setToken", () => {
    it("stores token in localStorage", () => {
      setToken("my-token");
      expect(localStorage.getItem("request_nest_admin_token")).toBe("my-token");
    });

    it("overwrites existing token", () => {
      setToken("first-token");
      setToken("second-token");
      expect(getToken()).toBe("second-token");
    });
  });

  describe("clearToken", () => {
    it("removes token from localStorage", () => {
      setToken("token-to-clear");
      clearToken();
      expect(getToken()).toBeNull();
    });

    it("does nothing if no token exists", () => {
      clearToken();
      expect(getToken()).toBeNull();
    });
  });

  describe("hasToken", () => {
    it("returns false when no token is stored", () => {
      expect(hasToken()).toBe(false);
    });

    it("returns true when token is stored", () => {
      setToken("test-token");
      expect(hasToken()).toBe(true);
    });
  });
});
