import pilotarrClient from "../lib/pilotarrClient";
import { mockIndexers, mockHistory, mockSearchResults } from "../pages/indexer/mockData";

// TODO: replace mock returns with real API calls once backend is wired
// All calls will go through /api/prowlarr/* on the Pilotarr backend

/**
 * Get all configured indexers with their stats
 * @returns {Promise<Array>} Indexers with embedded stats
 */
export const getIndexers = async () => {
  try {
    const response = await pilotarrClient?.get("/prowlarr/indexers");
    return response?.data || [];
  } catch {
    // Backend not wired yet — return mock data
    return mockIndexers;
  }
};

/**
 * Toggle enable/disable for a single indexer
 * @param {number} id - Indexer ID
 * @param {boolean} enable - New state
 * @returns {Promise<boolean>}
 */
export const toggleIndexer = async (id, enable) => {
  try {
    await pilotarrClient?.patch(`/prowlarr/indexers/${id}`, { enable });
    return true;
  } catch {
    // Mock: simulate success
    return true;
  }
};

/**
 * Get search/grab history
 * @param {number} limit
 * @returns {Promise<Array>}
 */
export const getHistory = async (limit = 20) => {
  try {
    const response = await pilotarrClient?.get(`/prowlarr/history?limit=${limit}`);
    return response?.data || [];
  } catch {
    return mockHistory.slice(0, limit);
  }
};

/**
 * Perform a live search across indexers
 * @param {string} query
 * @param {string} type - "search" | "tvsearch" | "moviesearch"
 * @returns {Promise<Array>}
 */
export const searchIndexers = async (query, type = "search") => {
  try {
    const params = new URLSearchParams({ query, type });
    const response = await pilotarrClient?.get(`/prowlarr/search?${params}`);
    return response?.data || [];
  } catch {
    // Mock: return mock results regardless of query
    await new Promise((r) => setTimeout(r, 600)); // simulate network delay
    return mockSearchResults;
  }
};

/**
 * Grab/download a search result
 * @param {string} guid - Result GUID
 * @param {string} indexerId - Indexer name/id
 * @returns {Promise<boolean>}
 */
export const grabResult = async (guid, indexerId) => {
  try {
    await pilotarrClient?.post("/prowlarr/grab", { guid, indexerId });
    return true;
  } catch {
    // Mock: simulate success
    await new Promise((r) => setTimeout(r, 400));
    return true;
  }
};
