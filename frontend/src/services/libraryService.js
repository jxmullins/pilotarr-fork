import pilotarrClient from "../lib/pilotarrClient";

/**
 * Get recent items (media and request) from dashboard API
 * @param {number} limit - Number of items to fetch
 * @param {string} sortBy - Sort field (added_date, ratio, size, title)
 * @param {string} sortOrder - Sort order (asc, desc)
 * @returns {Promise<Array>} Array of recent items
 */
export const getRecentItems = async (
  limit = 10,
  sortBy = "added_date",
  sortOrder = "desc",
) => {
  try {
    const response = await pilotarrClient?.get(
      `/dashboard/recent-items?limit=${limit}&sort_by=${sortBy}&sort_order=${sortOrder}`,
    );
    return response?.data || [];
  } catch (error) {
    console.error("Error fetching recent items:", error?.message);
    return [];
  }
};

/**
 * Get all library items
 * @param {number} limit - Number of items to fetch
 * @param {string} sortBy - Sort field (added_date, ratio, size, title)
 * @param {string} sortOrder - Sort order (asc, desc)
 * @returns {Promise<Array>} Array item
 */
export const getLibraryItems = async (
  limit = 20,
  sortBy = "added_date",
  sortOrder = "desc",
) => {
  try {
    const response = await pilotarrClient?.get(
      `/library?limit=${limit}&sort_by=${sortBy}&sort_order=${sortOrder}`,
    );
    return response?.data || [];
  } catch (error) {
    console.error("Error fetching library items:", error?.message);
    return [];
  }
};

/**
 * Get library item by id
 * @param {string} id - Media item ID
 * @returns {Promise<Object|null>} Media detail object or null
 */
export const getLibraryItemById = async (id) => {
  try {
    const response = await pilotarrClient?.get(`/library/${id}`);
    return response?.data || [];
  } catch (error) {
    console.error("Error fetching library items:", error?.message);
    return null;
  }
};

/**
 * Get all seasons with embedded episodes for a TV show (single request)
 * @param {string} id - Library item ID
 * @returns {Promise<Array>} Array of seasons with episodes
 */
export const getSeasonsWithEpisodes = async (id) => {
  try {
    const response = await pilotarrClient?.get(
      `/library/${id}/seasons-with-episodes`,
    );
    return response?.data || [];
  } catch (error) {
    console.error("Error fetching seasons with episodes:", error?.message);
    return [];
  }
};