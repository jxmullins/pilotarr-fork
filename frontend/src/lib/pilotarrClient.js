import axios from "axios";

const apiUrl = import.meta.env?.VITE_PILOTARR_API_URL;
const apiKey = import.meta.env?.VITE_PILOTARR_API_KEY;

if (!apiUrl || !apiKey) {
  console.warn(
    "Missing Pilotarr environment variables. Please check your .env file for VITE_PILOTARR_API_URL and VITE_PILOTARR_API_KEY",
  );
}

/**
 * Pilotarr API Client
 * Backend API for all data operations and service integrations
 */
export const PilotarrClient = axios?.create({
  baseURL: apiUrl,
  headers: {
    "X-API-Key": apiKey,
    "Content-Type": "application/json",
  },
  timeout: 30000,
});

// Add response interceptor for error handling
PilotarrClient?.interceptors?.response?.use(
  (response) => response,
  (error) => {
    // Only log errors that aren't 404s (those are handled by individual services)
    if (error?.response?.status !== 404) {
      // Only log if it's not a network error (API might be down)
      if (error?.code !== "ERR_NETWORK" && error?.message !== "Network Error") {
        console.error(
          "Pilotarr API Error:",
          error?.response?.data || error?.message,
        );
      }
    }
    return Promise.reject(error);
  },
);

export default PilotarrClient;
