import { describe, it, expect, beforeEach } from "vitest";
import { FakeBinApiClient, createFakeClientWithBins } from "./fakeClient";
import type { Bin } from "../types";

describe("FakeBinApiClient", () => {
  let client: FakeBinApiClient;

  beforeEach(() => {
    client = new FakeBinApiClient();
  });

  describe("listBins", () => {
    it("returns empty array when no bins exist", async () => {
      const bins = await client.listBins();
      expect(bins).toEqual([]);
    });

    it("returns all added bins", async () => {
      const bin1: Bin = {
        id: "b_test1",
        name: "Test Bin 1",
        ingest_url: "/b/test1",
        created_at: "2024-01-01T00:00:00Z",
      };
      const bin2: Bin = {
        id: "b_test2",
        name: "Test Bin 2",
        ingest_url: "/b/test2",
        created_at: "2024-01-02T00:00:00Z",
      };

      client.addBin(bin1);
      client.addBin(bin2);

      const bins = await client.listBins();
      expect(bins).toHaveLength(2);
      expect(bins).toContainEqual(bin1);
      expect(bins).toContainEqual(bin2);
    });
  });

  describe("createBin", () => {
    it("creates a bin with the given name", async () => {
      const bin = await client.createBin("My Webhook");

      expect(bin.name).toBe("My Webhook");
      expect(bin.id).toMatch(/^b_/);
      expect(bin.ingest_url).toMatch(/^\/b\//);
      expect(bin.created_at).toBeDefined();
    });

    it("creates a bin with null name", async () => {
      const bin = await client.createBin(null);

      expect(bin.name).toBeNull();
      expect(bin.id).toMatch(/^b_/);
    });

    it("adds created bin to the list", async () => {
      await client.createBin("Test");

      const bins = await client.listBins();
      expect(bins).toHaveLength(1);
      expect(bins[0].name).toBe("Test");
    });
  });

  describe("clear", () => {
    it("removes all bins", async () => {
      await client.createBin("Bin 1");
      await client.createBin("Bin 2");

      client.clear();

      const bins = await client.listBins();
      expect(bins).toEqual([]);
    });
  });

  describe("getBins", () => {
    it("returns current bins synchronously", async () => {
      await client.createBin("Test");

      const bins = client.getBins();
      expect(bins).toHaveLength(1);
    });
  });
});

describe("createFakeClientWithBins", () => {
  it("creates client with pre-populated bins", async () => {
    const bins: Bin[] = [
      {
        id: "b_pre1",
        name: "Pre-populated 1",
        ingest_url: "/b/pre1",
        created_at: "2024-01-01T00:00:00Z",
      },
      {
        id: "b_pre2",
        name: "Pre-populated 2",
        ingest_url: "/b/pre2",
        created_at: "2024-01-02T00:00:00Z",
      },
    ];

    const client = createFakeClientWithBins(bins);

    const result = await client.listBins();
    expect(result).toHaveLength(2);
    expect(result).toContainEqual(bins[0]);
    expect(result).toContainEqual(bins[1]);
  });
});
