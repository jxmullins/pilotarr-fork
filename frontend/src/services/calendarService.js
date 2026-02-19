import pilotarrClient from "../lib/pilotarrClient";

/**
 * Get calendar events for a date range
 * @param {string} start - Start date YYYY-MM-DD
 * @param {string} end - End date YYYY-MM-DD
 * @returns {Promise<Array>} Array of calendar events
 */
export const getCalendarEvents = async (start, end) => {
  try {
    const params = new URLSearchParams();
    if (start) params.append("start", start);
    if (end) params.append("end", end);

    const response = await pilotarrClient?.get(`/dashboard/calendar?${params}`);

    // Map snake_case API response to camelCase for frontend
    const events =
      response?.data?.map((event) => ({
        id: event?.id,
        title: event?.title,
        type: event?.media_type, // "tv" or "movie"
        eventType: "release", // all real events are releases
        releaseDate: event?.release_date,
        imageUrl: event?.image_url,
        imageAlt: event?.image_alt,
        episode: event?.episode,
        status: event?.status,
      })) || [];

    return events;
  } catch (error) {
    return [];
  }
};

/**
 * Add new calendar event
 * @param {Object} event - Calendar event data
 * @returns {Promise<Object|null>} Created calendar event or null
 */
export const addCalendarEvent = async (event) => {
  try {
    const response = await pilotarrClient?.post("/calendar/events", event);
    return response?.data || null;
  } catch (error) {
    return null;
  }
};

/**
 * Update calendar event status
 * @param {string} id - Calendar event ID
 * @param {string} status - New status
 * @returns {Promise<boolean>} Success status
 */
export const updateCalendarEventStatus = async (id, status) => {
  try {
    await pilotarrClient?.patch(`/calendar/events/${id}`, { status });
    return true;
  } catch (error) {
    return false;
  }
};

/**
 * Delete calendar event
 * @param {string} id - Calendar event ID
 * @returns {Promise<boolean>} Success status
 */
export const deleteCalendarEvent = async (id) => {
  try {
    await pilotarrClient?.delete(`/calendar/events/${id}`);
    return true;
  } catch (error) {
    return false;
  }
};
