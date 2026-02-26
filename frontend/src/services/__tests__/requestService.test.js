import { describe, it, expect, vi, beforeEach } from "vitest";

vi.mock("../../lib/pilotarrClient", () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    delete: vi.fn(),
    patch: vi.fn(),
  },
}));

import pilotarrClient from "../../lib/pilotarrClient";
import {
  getJellyseerrRequests,
  approveRequest,
  declineRequest,
  deleteJellyseerrRequest,
  updateRequestPriority,
} from "../requestService";

beforeEach(() => {
  vi.clearAllMocks();
});

// ── getJellyseerrRequests ─────────────────────────────────────────────────────

describe("getJellyseerrRequests", () => {
  it("maps snake_case API response to camelCase", async () => {
    pilotarrClient.get.mockResolvedValue({
      data: [
        {
          id: "abc",
          title: "Inception",
          media_type: "movie",
          requested_by: "alice",
          requested_date: "2025-01-10",
          status: 1,
          image_url: "https://example.com/poster.jpg",
          image_alt: "Inception poster",
          year: 2010,
          description: "A thriller.",
          priority: "medium",
          quality: "HD-1080p",
        },
      ],
    });

    const result = await getJellyseerrRequests();

    expect(result).toHaveLength(1);
    expect(result[0]).toMatchObject({
      id: "abc",
      title: "Inception",
      mediaType: "movie",
      requestedBy: "alice",
      requestedDate: "2025-01-10",
      status: 1,
      imageUrl: "https://example.com/poster.jpg",
      imageAlt: "Inception poster",
      year: 2010,
      description: "A thriller.",
      priority: "medium",
      quality: "HD-1080p",
    });
  });

  it("calls correct URL with default params", async () => {
    pilotarrClient.get.mockResolvedValue({ data: [] });
    await getJellyseerrRequests();
    expect(pilotarrClient.get).toHaveBeenCalledWith(expect.stringContaining("/dashboard/requests"));
  });

  it("passes status and limit query params", async () => {
    pilotarrClient.get.mockResolvedValue({ data: [] });
    await getJellyseerrRequests("pending", 50);
    const url = pilotarrClient.get.mock.calls[0][0];
    expect(url).toContain("status=pending");
    expect(url).toContain("limit=50");
  });

  it("returns empty array on API error", async () => {
    pilotarrClient.get.mockRejectedValue(new Error("Network error"));
    const result = await getJellyseerrRequests();
    expect(result).toEqual([]);
  });

  it("returns empty array when response data is null", async () => {
    pilotarrClient.get.mockResolvedValue({ data: null });
    const result = await getJellyseerrRequests();
    expect(result).toEqual([]);
  });
});

// ── approveRequest ────────────────────────────────────────────────────────────

describe("approveRequest", () => {
  it("posts to the correct approve endpoint", async () => {
    pilotarrClient.post.mockResolvedValue({});
    await approveRequest("req-123");
    expect(pilotarrClient.post).toHaveBeenCalledWith("/jellyseerr/requests/req-123/approve");
  });

  it("returns true on success", async () => {
    pilotarrClient.post.mockResolvedValue({});
    const result = await approveRequest("req-123");
    expect(result).toBe(true);
  });

  it("returns false on API error", async () => {
    pilotarrClient.post.mockRejectedValue(new Error("503"));
    const result = await approveRequest("req-123");
    expect(result).toBe(false);
  });
});

// ── declineRequest ────────────────────────────────────────────────────────────

describe("declineRequest", () => {
  it("posts to the correct decline endpoint", async () => {
    pilotarrClient.post.mockResolvedValue({});
    await declineRequest("req-456");
    expect(pilotarrClient.post).toHaveBeenCalledWith("/jellyseerr/requests/req-456/decline");
  });

  it("returns true on success", async () => {
    pilotarrClient.post.mockResolvedValue({});
    const result = await declineRequest("req-456");
    expect(result).toBe(true);
  });

  it("returns false on API error", async () => {
    pilotarrClient.post.mockRejectedValue(new Error("500"));
    const result = await declineRequest("req-456");
    expect(result).toBe(false);
  });
});

// ── deleteJellyseerrRequest ───────────────────────────────────────────────────

describe("deleteJellyseerrRequest", () => {
  it("calls DELETE on the correct endpoint", async () => {
    pilotarrClient.delete.mockResolvedValue({});
    await deleteJellyseerrRequest("req-789");
    expect(pilotarrClient.delete).toHaveBeenCalledWith("/jellyseerr/requests/req-789");
  });

  it("returns true on success", async () => {
    pilotarrClient.delete.mockResolvedValue({});
    expect(await deleteJellyseerrRequest("req-789")).toBe(true);
  });

  it("returns false on error", async () => {
    pilotarrClient.delete.mockRejectedValue(new Error("fail"));
    expect(await deleteJellyseerrRequest("req-789")).toBe(false);
  });
});

// ── updateRequestPriority ─────────────────────────────────────────────────────

describe("updateRequestPriority", () => {
  it("patches the correct endpoint with priority", async () => {
    pilotarrClient.patch.mockResolvedValue({});
    await updateRequestPriority("req-001", "high");
    expect(pilotarrClient.patch).toHaveBeenCalledWith("/jellyseerr/requests/req-001", {
      priority: "high",
    });
  });

  it("returns true on success", async () => {
    pilotarrClient.patch.mockResolvedValue({});
    expect(await updateRequestPriority("req-001", "low")).toBe(true);
  });

  it("returns false on error", async () => {
    pilotarrClient.patch.mockRejectedValue(new Error("fail"));
    expect(await updateRequestPriority("req-001", "high")).toBe(false);
  });
});
