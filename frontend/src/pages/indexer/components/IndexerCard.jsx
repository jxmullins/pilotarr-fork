import React, { useState } from "react";
import Icon from "../../../components/AppIcon";
import { toggleIndexer } from "../../../services/prowlarrService";

const protocolColors = {
  torrent: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  usenet: "bg-blue-500/10 text-blue-400 border-blue-500/20",
};

const privacyColors = {
  public: "bg-slate-500/10 text-slate-400 border-slate-500/20",
  private: "bg-amber-500/10 text-amber-400 border-amber-500/20",
  semi_private: "bg-orange-500/10 text-orange-400 border-orange-500/20",
};

const getHealthColor = (indexer) => {
  if (!indexer.enable) return "text-muted-foreground";
  const total = indexer.stats.numberOfQueries;
  if (total === 0) return "text-muted-foreground";
  const failRate = indexer.stats.numberOfFailedQueries / total;
  if (failRate > 0.15) return "text-red-400";
  if (failRate > 0.05) return "text-amber-400";
  return "text-emerald-400";
};

const getHealthDot = (indexer) => {
  if (!indexer.enable) return "bg-slate-600";
  const total = indexer.stats.numberOfQueries;
  if (total === 0) return "bg-slate-600";
  const failRate = indexer.stats.numberOfFailedQueries / total;
  if (failRate > 0.15) return "bg-red-500";
  if (failRate > 0.05) return "bg-amber-500";
  return "bg-emerald-500";
};

const formatMs = (ms) => {
  if (!ms || ms === 0) return "—";
  if (ms >= 1000) return `${(ms / 1000).toFixed(1)}s`;
  return `${ms}ms`;
};

const IndexerCard = ({ indexer, onToggle }) => {
  const [loading, setLoading] = useState(false);
  const [enabled, setEnabled] = useState(indexer.enable);

  const handleToggle = async () => {
    setLoading(true);
    const newState = !enabled;
    setEnabled(newState); // optimistic
    const ok = await toggleIndexer(indexer.id, newState);
    if (!ok) setEnabled(!newState); // revert on error
    setLoading(false);
    onToggle?.(indexer.id, newState);
  };

  const failRate =
    indexer.stats.numberOfQueries > 0
      ? Math.round((indexer.stats.numberOfFailedQueries / indexer.stats.numberOfQueries) * 100)
      : 0;

  return (
    <div
      className={`bg-card border rounded-lg p-4 flex flex-col gap-3 transition-opacity ${
        enabled ? "border-border opacity-100" : "border-border/50 opacity-60"
      }`}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2 min-w-0">
          <div className={`w-2 h-2 rounded-full flex-shrink-0 ${getHealthDot(indexer)}`} />
          <span className="font-semibold text-foreground truncate">{indexer.name}</span>
        </div>

        {/* Toggle */}
        <button
          onClick={handleToggle}
          disabled={loading}
          className={`relative flex-shrink-0 w-10 h-5 rounded-full transition-colors focus:outline-none ${
            enabled ? "bg-primary" : "bg-slate-700"
          } ${loading ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}`}
          aria-label={enabled ? "Disable indexer" : "Enable indexer"}
        >
          <span
            className={`absolute top-0.5 left-0.5 w-4 h-4 rounded-full bg-white shadow transition-transform ${
              enabled ? "translate-x-5" : "translate-x-0"
            }`}
          />
        </button>
      </div>

      {/* Badges */}
      <div className="flex flex-wrap gap-1.5">
        <span
          className={`text-xs px-2 py-0.5 rounded border font-medium ${protocolColors[indexer.protocol] || protocolColors.torrent}`}
        >
          {indexer.protocol}
        </span>
        <span
          className={`text-xs px-2 py-0.5 rounded border font-medium ${privacyColors[indexer.privacy] || privacyColors.public}`}
        >
          {indexer.privacy}
        </span>
      </div>

      {/* Categories */}
      <div className="flex flex-wrap gap-1">
        {indexer.capabilities.categories.slice(0, 4).map((cat) => (
          <span
            key={cat}
            className="text-xs text-muted-foreground bg-background px-1.5 py-0.5 rounded"
          >
            {cat}
          </span>
        ))}
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-2 pt-1 border-t border-border/50">
        <div className="text-center">
          <p className="text-xs text-muted-foreground">Queries</p>
          <p className="text-sm font-semibold text-foreground">
            {indexer.stats.numberOfQueries.toLocaleString()}
          </p>
        </div>
        <div className="text-center">
          <p className="text-xs text-muted-foreground">Fail rate</p>
          <p className={`text-sm font-semibold ${getHealthColor(indexer)}`}>
            {indexer.stats.numberOfQueries > 0 ? `${failRate}%` : "—"}
          </p>
        </div>
        <div className="text-center">
          <p className="text-xs text-muted-foreground">Avg time</p>
          <p className="text-sm font-semibold text-foreground">
            {formatMs(indexer.stats.averageResponseTime)}
          </p>
        </div>
      </div>
    </div>
  );
};

export default IndexerCard;
