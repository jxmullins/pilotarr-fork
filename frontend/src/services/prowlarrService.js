import pilotarrClient from "../lib/pilotarrClient";

export const getIndexers = async () => {
  const response = await pilotarrClient.get("/prowlarr/indexers");
  return response.data || [];
};

export const toggleIndexer = async (id, enable) => {
  try {
    await pilotarrClient.patch(`/prowlarr/indexers/${id}`, { enable });
    return true;
  } catch {
    return false;
  }
};

export const getHistory = async (limit = 20) => {
  const response = await pilotarrClient.get(`/prowlarr/history?limit=${limit}`);
  return response.data || [];
};

export const searchIndexers = async (query, type = "search") => {
  const params = new URLSearchParams({ query, type });
  const response = await pilotarrClient.get(`/prowlarr/search?${params}`);
  return response.data || [];
};

export const grabResult = async (guid, indexerId) => {
  try {
    await pilotarrClient.post("/prowlarr/grab", { guid, indexerId });
    return true;
  } catch {
    return false;
  }
};
