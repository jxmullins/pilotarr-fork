import React from "react";
import Icon from "../../../components/AppIcon";

const formatTimeAgo = (dateStr) => {
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "Just now";
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
};

const EventBadge = ({ eventType, successful }) => {
  const isGrab = eventType === "grab";
  return (
    <span
      className={`inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded border font-medium ${
        !successful
          ? "bg-red-500/10 text-red-400 border-red-500/20"
          : isGrab
            ? "bg-amber-500/10 text-amber-400 border-amber-500/20"
            : "bg-slate-500/10 text-slate-400 border-slate-500/20"
      }`}
    >
      <Icon name={!successful ? "AlertCircle" : isGrab ? "Download" : "Search"} size={11} />
      {!successful ? "Failed" : isGrab ? "Grabbed" : "Searched"}
    </span>
  );
};

const SearchHistory = ({ history, onRefresh, loading }) => {
  if (!history.length) {
    return (
      <div className="text-center py-8 text-muted-foreground text-sm flex flex-col items-center gap-3">
        <span>No history yet</span>
        {onRefresh && (
          <button
            onClick={onRefresh}
            disabled={loading}
            className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded bg-card border border-border text-muted-foreground hover:text-foreground transition-colors disabled:opacity-50"
          >
            <Icon name="RefreshCw" size={13} className={loading ? "animate-spin" : ""} />
            Refresh
          </button>
        )}
      </div>
    );
  }

  return (
    <div>
      {onRefresh && (
        <div className="flex justify-end px-4 py-2 border-b border-border/50">
          <button
            onClick={onRefresh}
            disabled={loading}
            className="flex items-center gap-1.5 text-xs px-2.5 py-1 rounded border border-border text-muted-foreground hover:text-foreground transition-colors disabled:opacity-50"
          >
            <Icon name="RefreshCw" size={12} className={loading ? "animate-spin" : ""} />
            Refresh
          </button>
        </div>
      )}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border/50">
              <th className="text-left px-4 py-2.5 text-xs text-muted-foreground font-medium">
                When
              </th>
              <th className="text-left px-3 py-2.5 text-xs text-muted-foreground font-medium">
                Query
              </th>
              <th className="text-left px-3 py-2.5 text-xs text-muted-foreground font-medium hidden md:table-cell">
                Indexer
              </th>
              <th className="text-left px-3 py-2.5 text-xs text-muted-foreground font-medium hidden sm:table-cell">
                Category
              </th>
              <th className="text-center px-3 py-2.5 text-xs text-muted-foreground font-medium">
                Event
              </th>
            </tr>
          </thead>
          <tbody>
            {history.map((entry, i) => (
              <tr
                key={entry.id}
                className={`border-b border-border/30 hover:bg-background/50 transition-colors ${
                  i === history.length - 1 ? "border-b-0" : ""
                }`}
              >
                <td className="px-4 py-2.5 text-muted-foreground whitespace-nowrap text-xs">
                  {formatTimeAgo(entry.date)}
                </td>
                <td className="px-3 py-2.5 text-foreground max-w-[200px] md:max-w-xs">
                  <span className="truncate block" title={entry.query}>
                    {entry.query}
                  </span>
                </td>
                <td className="px-3 py-2.5 hidden md:table-cell">
                  <span className="text-xs text-muted-foreground bg-background px-1.5 py-0.5 rounded whitespace-nowrap">
                    {entry.indexer}
                  </span>
                </td>
                <td className="px-3 py-2.5 hidden sm:table-cell">
                  <span className="text-xs text-muted-foreground">
                    {entry.categories?.join(", ") || "—"}
                  </span>
                </td>
                <td className="px-3 py-2.5 text-center">
                  <EventBadge eventType={entry.eventType} successful={entry.successful} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default SearchHistory;
