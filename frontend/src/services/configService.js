import pilotarrClient from "../lib/pilotarrClient";

/**
 * Service Configuration Operations
 */

// Helper function to convert API response to camelCase
const mapServiceResponse = (data) => {
  if (!data) return null;

  return {
    serviceName: data?.service_name,
    url: data?.url,
    username: data?.username, // Not sensitive — returned by API
    port: data?.port,
    isActive: data?.is_active,
    id: data?.id,
    lastTestedAt: data?.last_tested_at,
    testStatus: data?.test_status,
    testMessage: data?.test_message,
    createdAt: data?.created_at,
    updatedAt: data?.updated_at,
    // Credential presence flags — the actual secrets are never returned
    hasApiKey: data?.has_api_key ?? false,
    hasPassword: data?.has_password ?? false,
  };
};

// Get all service configurations
export const getServiceConfigurations = async () => {
  try {
    // Fetch all services individually since the API uses /api/services/{service_name}
    const serviceNames = ["jellyfin", "jellyseerr", "radarr", "sonarr", "qbittorrent", "prowlarr"];
    const promises = serviceNames?.map((name) =>
      pilotarrClient
        ?.get(`/services/${name}`)
        ?.then((response) => mapServiceResponse(response?.data))
        ?.catch((error) => {
          // If service not found (404), return null
          if (error?.response?.status === 404) {
            return null;
          }
          throw error;
        }),
    );

    const results = await Promise?.all(promises);
    return results?.filter((config) => config !== null);
  } catch (error) {
    console.error("Error fetching service configurations:", error?.message);
    return [];
  }
};

// Get single service configuration by service name
export const getServiceConfiguration = async (serviceName) => {
  try {
    const response = await pilotarrClient?.get(`/services/${serviceName}`);
    return mapServiceResponse(response?.data);
  } catch (error) {
    console.error(`Error fetching ${serviceName} configuration:`, error?.message);
    return null;
  }
};

export const saveServiceConfiguration = async (serviceName, config) => {
  try {
    const payload = {
      service_name: serviceName,
      url: config?.url,
      username: config?.username || null,
      port: config?.port ? parseInt(config?.port) : null,
      is_active: config?.isActive !== undefined ? config?.isActive : false,
    };

    // Only send credentials when the user explicitly provided a new value.
    // Empty/absent values are intentionally omitted so the backend keeps the
    // previously stored secret unchanged.
    if (config?.apiKey) payload.api_key = config.apiKey;
    if (config?.password) payload.password = config.password;

    const response = await pilotarrClient?.put(`/services/${serviceName}`, payload);
    return mapServiceResponse(response?.data);
  } catch (error) {
    console.error(`Error saving ${serviceName} configuration:`, error?.message);
    throw error;
  }
};

// Test service connection
export const testServiceConnection = async (serviceName) => {
  try {
    const response = await pilotarrClient?.post(`/services/${serviceName}/test`, {});
    return {
      success: response?.data?.success,
      message: response?.data?.message,
      testedAt: response?.data?.tested_at,
    };
  } catch (error) {
    console.error(`Error testing ${serviceName} connection:`, error?.message);
    throw error;
  }
};

// Update test status for a service
export const updateServiceTestStatus = async (serviceName, testStatus, testMessage) => {
  try {
    const response = await pilotarrClient?.patch(`/services/${serviceName}/test`, {
      test_status: testStatus,
      test_message: testMessage,
      last_tested_at: new Date()?.toISOString(),
    });
    return mapServiceResponse(response?.data);
  } catch (error) {
    console.error("Error updating test status:", error?.message);
    throw error;
  }
};

// Delete service configuration
export const deleteServiceConfiguration = async (serviceName) => {
  try {
    await pilotarrClient?.delete(`/services/${serviceName}`);
    return true;
  } catch (error) {
    console.error("Error deleting service configuration:", error?.message);
    return false;
  }
};

export default {
  getServiceConfigurations,
  getServiceConfiguration,
  saveServiceConfiguration,
  testServiceConnection,
  updateServiceTestStatus,
  deleteServiceConfiguration,
};
