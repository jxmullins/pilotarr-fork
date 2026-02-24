import React, { useState, useEffect } from "react";
import Icon from "../../../components/AppIcon";
import Input from "../../../components/ui/Input";
import Button from "../../../components/ui/Button";

const ServiceCard = ({ service, onTest, onConfigChange, testStatus }) => {
  const [showApiKey, setShowApiKey] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [config, setConfig] = useState({
    url: service?.url || "",
    apiKey: "", // Never pre-filled — API never returns the actual key
    username: service?.username || "",
    password: "", // Never pre-filled — API never returns the actual password
    port: service?.port || "",
    hasApiKey: service?.hasApiKey || false,
    hasPassword: service?.hasPassword || false,
  });

  const isQBittorrent = service?.id === "qbittorrent";

  // Update local state when service prop changes (after API data loads)
  useEffect(() => {
    setConfig({
      url: service?.url || "",
      apiKey: "",
      username: service?.username || "",
      password: "",
      port: service?.port || "",
      hasApiKey: service?.hasApiKey || false,
      hasPassword: service?.hasPassword || false,
    });
  }, [service?.url, service?.username, service?.port, service?.hasApiKey, service?.hasPassword]);

  const handleInputChange = (field, value) => {
    const updatedConfig = { ...config, [field]: value };
    setConfig(updatedConfig);
    onConfigChange(service?.id, updatedConfig);
  };

  const getStatusColor = () => {
    if (!testStatus) return "text-muted-foreground";
    switch (testStatus?.status) {
      case "success":
        return "text-success";
      case "error":
        return "text-error";
      case "testing":
        return "text-warning";
      default:
        return "text-muted-foreground";
    }
  };

  const getStatusIcon = () => {
    if (!testStatus) return "Circle";
    switch (testStatus?.status) {
      case "success":
        return "CheckCircle2";
      case "error":
        return "XCircle";
      case "testing":
        return "Loader2";
      default:
        return "Circle";
    }
  };

  const isConfigValid = isQBittorrent
    ? config?.url && config?.username && (config?.password || config?.hasPassword)
    : config?.url && (config?.apiKey || config?.hasApiKey);

  return (
    <div className="bg-card border border-border rounded-lg p-4 md:p-6 shadow-elevation-2 transition-smooth hover:shadow-elevation-3">
      <div className="flex items-start justify-between mb-4 md:mb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 md:w-12 md:h-12 rounded-lg flex items-center justify-center bg-primary/10">
            <Icon
              name={service?.icon}
              size={20}
              color="var(--color-primary)"
              className="md:w-6 md:h-6"
            />
          </div>
          <div>
            <h3 className="text-base md:text-lg font-semibold text-foreground">{service?.name}</h3>
            <p className="text-xs md:text-sm text-muted-foreground">{service?.description}</p>
          </div>
        </div>
        <div className={`flex items-center gap-2 ${getStatusColor()}`}>
          <Icon
            name={getStatusIcon()}
            size={18}
            className={testStatus?.status === "testing" ? "animate-spin" : ""}
          />
          <span className="text-xs md:text-sm font-medium hidden sm:inline">
            {testStatus?.status === "success" && "Connected"}
            {testStatus?.status === "error" && "Failed"}
            {testStatus?.status === "testing" && "Testing..."}
            {!testStatus && "Not Tested"}
          </span>
        </div>
      </div>
      <div className="space-y-3 md:space-y-4">
        <Input
          label="Server URL"
          type="url"
          placeholder="https://example.com"
          value={config?.url}
          onChange={(e) => handleInputChange("url", e?.target?.value)}
          required
          description="Full URL including protocol (http:// or https://)"
        />

        {isQBittorrent ? (
          <>
            <Input
              label="Username"
              type="text"
              placeholder="Enter your username"
              value={config?.username}
              onChange={(e) => handleInputChange("username", e?.target?.value)}
              required
              description="qBittorrent Web UI username"
            />

            <div className="relative">
              <Input
                label="Password"
                type={showPassword ? "text" : "password"}
                placeholder={
                  config?.hasPassword ? "Saved — enter new value to change" : "Enter your password"
                }
                value={config?.password}
                onChange={(e) => handleInputChange("password", e?.target?.value)}
                required={!config?.hasPassword}
                description="qBittorrent Web UI password"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-9 text-muted-foreground hover:text-foreground transition-colors"
                aria-label={showPassword ? "Hide password" : "Show password"}
              >
                <Icon name={showPassword ? "EyeOff" : "Eye"} size={18} />
              </button>
            </div>
          </>
        ) : (
          <div className="relative">
            <Input
              label="API Key"
              type={showApiKey ? "text" : "password"}
              placeholder={
                config?.hasApiKey ? "Saved — enter new value to change" : "Enter your API key"
              }
              value={config?.apiKey}
              onChange={(e) => handleInputChange("apiKey", e?.target?.value)}
              required={!config?.hasApiKey}
              description="Found in service settings under API section"
            />
            <button
              type="button"
              onClick={() => setShowApiKey(!showApiKey)}
              className="absolute right-3 top-9 text-muted-foreground hover:text-foreground transition-colors"
              aria-label={showApiKey ? "Hide API key" : "Show API key"}
            >
              <Icon name={showApiKey ? "EyeOff" : "Eye"} size={18} />
            </button>
          </div>
        )}

        <Input
          label="Port (Optional)"
          type="number"
          placeholder={isQBittorrent ? "8080" : "8989"}
          value={config?.port}
          onChange={(e) => handleInputChange("port", e?.target?.value)}
          description="Leave empty to use default port"
        />

        {testStatus?.message && (
          <div
            className={`p-3 rounded-lg text-sm ${
              testStatus?.status === "success"
                ? "bg-success/10 text-success border border-success/20"
                : testStatus?.status === "error"
                  ? "bg-error/10 text-error border border-error/20"
                  : "bg-warning/10 text-warning border border-warning/20"
            }`}
          >
            <p className="font-medium">{testStatus?.message}</p>
            {testStatus?.details && (
              <p className="text-xs mt-1 opacity-80">{testStatus?.details}</p>
            )}
          </div>
        )}

        <Button
          variant="outline"
          onClick={() => onTest(service?.id, config)}
          disabled={!isConfigValid || testStatus?.status === "testing"}
          loading={testStatus?.status === "testing"}
          iconName="Zap"
          iconPosition="left"
          fullWidth
        >
          Test Connection
        </Button>
      </div>
      {(config?.apiKey || config?.hasApiKey || config?.password || config?.hasPassword) && (
        <div className="mt-4 flex items-center gap-2 text-xs text-muted-foreground">
          <Icon name="Shield" size={14} />
          <span>{isQBittorrent ? "Credentials" : "API key"} will be encrypted before storage</span>
        </div>
      )}
    </div>
  );
};

export default ServiceCard;
