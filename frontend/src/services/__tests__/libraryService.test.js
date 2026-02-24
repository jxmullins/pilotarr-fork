import { describe, it, expect, vi, beforeEach } from "vitest";

vi.mock("../../lib/pilotarrClient", () => ({
  default: {
    get: vi.fn(),
    patch: vi.fn(),
    post: vi.fn(),
  },
}));

import pilotarrClient from "../../lib/pilotarrClient";
import {
  getLibraryItems,
  getLibraryItemById,
  getSeasonsWithEpisodes,
  setEpisodeWatched,
  setSeasonWatched,
  monitorEpisode,
  searchEpisode,
} from "../libraryService";

beforeEach(() => {
  vi.clearAllMocks();
});

describe("getLibraryItems", () => {
  it("returns data from API", async () => {
    pilotarrClient.get.mockResolvedValue({ data: [{ id: 1, title: "Movie" }] });
    const result = await getLibraryItems();
    expect(result).toEqual([{ id: 1, title: "Movie" }]);
    expect(pilotarrClient.get).toHaveBeenCalledWith(expect.stringContaining("/library"));
  });

  it("returns empty array on error", async () => {
    pilotarrClient.get.mockRejectedValue(new Error("fail"));
    const result = await getLibraryItems();
    expect(result).toEqual([]);
  });

  it("passes sort params in URL", async () => {
    pilotarrClient.get.mockResolvedValue({ data: [] });
    await getLibraryItems(10, "title", "asc");
    expect(pilotarrClient.get).toHaveBeenCalledWith(expect.stringContaining("sort_by=title"));
  });
});

describe("getLibraryItemById", () => {
  it("returns item data", async () => {
    pilotarrClient.get.mockResolvedValue({ data: { id: 5, title: "Show" } });
    const result = await getLibraryItemById(5);
    expect(result).toEqual({ id: 5, title: "Show" });
    expect(pilotarrClient.get).toHaveBeenCalledWith("/library/5");
  });

  it("returns null on error", async () => {
    pilotarrClient.get.mockRejectedValue(new Error("404"));
    const result = await getLibraryItemById(999);
    expect(result).toBeNull();
  });
});

describe("getSeasonsWithEpisodes", () => {
  it("returns seasons array", async () => {
    const seasons = [{ season_number: 1, episodes: [] }];
    pilotarrClient.get.mockResolvedValue({ data: seasons });
    const result = await getSeasonsWithEpisodes(1);
    expect(result).toEqual(seasons);
    expect(pilotarrClient.get).toHaveBeenCalledWith("/library/1/seasons-with-episodes");
  });

  it("returns empty array on error", async () => {
    pilotarrClient.get.mockRejectedValue(new Error("fail"));
    expect(await getSeasonsWithEpisodes(1)).toEqual([]);
  });
});

describe("setEpisodeWatched", () => {
  it("patches the correct endpoint and returns true", async () => {
    pilotarrClient.patch.mockResolvedValue({});
    const result = await setEpisodeWatched(1, 2, 3, true);
    expect(result).toBe(true);
    expect(pilotarrClient.patch).toHaveBeenCalledWith("/library/1/seasons/2/episodes/3/watched", {
      watched: true,
    });
  });

  it("returns false on error", async () => {
    pilotarrClient.patch.mockRejectedValue(new Error("fail"));
    expect(await setEpisodeWatched(1, 1, 1, true)).toBe(false);
  });
});

describe("setSeasonWatched", () => {
  it("patches season watched and returns true", async () => {
    pilotarrClient.patch.mockResolvedValue({});
    const result = await setSeasonWatched(1, 2, false);
    expect(result).toBe(true);
    expect(pilotarrClient.patch).toHaveBeenCalledWith("/library/1/seasons/2/watched", {
      watched: false,
    });
  });
});

describe("monitorEpisode", () => {
  it("posts to monitor endpoint and returns true", async () => {
    pilotarrClient.post.mockResolvedValue({});
    const result = await monitorEpisode(1, 2, 3);
    expect(result).toBe(true);
    expect(pilotarrClient.post).toHaveBeenCalledWith("/library/1/seasons/2/episodes/3/monitor");
  });

  it("returns false on error", async () => {
    pilotarrClient.post.mockRejectedValue(new Error("fail"));
    expect(await monitorEpisode(1, 1, 1)).toBe(false);
  });
});

describe("searchEpisode", () => {
  it("posts to search endpoint and returns true", async () => {
    pilotarrClient.post.mockResolvedValue({});
    const result = await searchEpisode(1, 2, 3);
    expect(result).toBe(true);
    expect(pilotarrClient.post).toHaveBeenCalledWith("/library/1/seasons/2/episodes/3/search");
  });

  it("returns false on error", async () => {
    pilotarrClient.post.mockRejectedValue(new Error("fail"));
    expect(await searchEpisode(1, 1, 1)).toBe(false);
  });
});
