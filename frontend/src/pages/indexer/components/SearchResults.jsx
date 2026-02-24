import React, { useState } from "react";
import Icon from "../../../components/AppIcon";
import { grabResult } from "../../../services/prowlarrService";

const formatSize = (bytes) => {
  if (!bytes) return "—";
  const gb = bytes / 1024 ** 3;
  if (gb >= 1) return `${gb.toFixed(1)} GB`;
  const mb = bytes / 1024 ** 2;
  return `${mb.toFixed(0)} MB`;
};

const formatAge = (dateStr) => {
  const diff = Date.now() - new Date(dateStr).getTime();
  const days = Math.floor(diff / (1000 * 3600 * 24));
  if (days === 0) return "Today";
  if (days === 1) return "1d";
  if (days < 30) return `${days}d`;
  const months = Math.floor(days / 30);
  return `${months}mo`;
};

const SeederBadge = ({ seeders }) => {
  if (seeders === null || seeders === undefined)
    return <span className="text-muted-foreground">—</span>;
  const color =
    seeders >= 100 ? "text-emerald-400" : seeders >= 10 ? "text-amber-400" : "text-red-400";
  return (
    <span className={`flex items-center gap-1 ${color}`}>
      <Icon name="ArrowUp" size={12} />
      {seeders}
    </span>
  );
};

const ProtocolBadge = ({ protocol }) => (
  <span
    className={`text-xs px-1.5 py-0.5 rounded border font-medium ${
      protocol === "torrent"
        ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
        : "bg-blue-500/10 text-blue-400 border-blue-500/20"
    }`}
  >
    {protocol === "torrent" ? "TOR" : "NZB"}
  </span>
);

const GrabButton = ({ result }) => {
  const [state, setState] = useState("idle"); // idle | loading | done | error

  const handleGrab = async () => {
    setState("loading");
    const ok = await grabResult(result.guid, result.indexer);
    setState(ok ? "done" : "error");
  };

  if (state === "done")
    return (
      <span className="flex items-center gap-1 text-xs text-emerald-400 font-medium">
        <Icon name="Check" size={14} />
        Grabbed
      </span>
    );

  if (state === "error")
    return (
      <span className="flex items-center gap-1 text-xs text-red-400 font-medium">
        <Icon name="X" size={14} />
        Failed
      </span>
    );

  return (
    <button
      onClick={handleGrab}
      disabled={state === "loading"}
      className="flex items-center gap-1 text-xs px-2.5 py-1.5 rounded bg-primary/10 text-primary border border-primary/20 hover:bg-primary/20 transition-colors font-medium disabled:opacity-50"
    >
      {state === "loading" ? (
        <div className="w-3 h-3 border-2 border-primary/30 border-t-primary rounded-full animate-spin" />
      ) : (
        <Icon name="Download" size={13} />
      )}
      Grab
    </button>
  );
};

const SearchResults = ({ results, query }) => {
  const [sortBy, setSortBy] = useState("seeders");

  const sorted = [...results].sort((a, b) => {
    if (sortBy === "seeders") return (b.seeders ?? -1) - (a.seeders ?? -1);
    if (sortBy === "size") return (b.size ?? 0) - (a.size ?? 0);
    if (sortBy === "age") return new Date(b.publishDate) - new Date(a.publishDate);
    return 0;
  });

  return (
    <div className="bg-card border border-border rounded-lg overflow-hidden">
      {/* Results header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border">
        <div className="flex items-center gap-2">
          <Icon name="List" size={16} color="var(--color-primary)" />
          <span className="text-sm font-semibold text-foreground">
            {results.length} result{results.length !== 1 ? "s" : ""}
          </span>
          {query && (
            <span className="text-xs text-muted-foreground">
              for &quot;<span className="text-foreground">{query}</span>&quot;
            </span>
          )}
        </div>

        <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
          <span>Sort:</span>
          {["seeders", "size", "age"].map((s) => (
            <button
              key={s}
              onClick={() => setSortBy(s)}
              className={`px-2 py-1 rounded transition-colors capitalize ${
                sortBy === s ? "bg-primary/10 text-primary" : "hover:text-foreground"
              }`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border/50">
              <th className="text-left px-4 py-2.5 text-xs text-muted-foreground font-medium w-1/2">
                Title
              </th>
              <th className="text-left px-3 py-2.5 text-xs text-muted-foreground font-medium">
                Indexer
              </th>
              <th className="text-right px-3 py-2.5 text-xs text-muted-foreground font-medium">
                Size
              </th>
              <th className="text-right px-3 py-2.5 text-xs text-muted-foreground font-medium">
                Seeds
              </th>
              <th className="text-right px-3 py-2.5 text-xs text-muted-foreground font-medium">
                Age
              </th>
              <th className="px-3 py-2.5" />
            </tr>
          </thead>
          <tbody>
            {sorted.map((result, i) => (
              <tr
                key={result.guid}
                className={`border-b border-border/30 hover:bg-background/50 transition-colors ${
                  i === sorted.length - 1 ? "border-b-0" : ""
                }`}
              >
                {/* Title */}
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2 min-w-0">
                    <ProtocolBadge protocol={result.protocol} />
                    <span className="text-foreground truncate max-w-xs" title={result.title}>
                      {result.title}
                    </span>
                  </div>
                </td>

                {/* Indexer */}
                <td className="px-3 py-3">
                  <span className="text-xs text-muted-foreground bg-background px-2 py-1 rounded whitespace-nowrap">
                    {result.indexer}
                  </span>
                </td>

                {/* Size */}
                <td className="px-3 py-3 text-right text-muted-foreground whitespace-nowrap">
                  {formatSize(result.size)}
                </td>

                {/* Seeders */}
                <td className="px-3 py-3 text-right">
                  <SeederBadge seeders={result.seeders} />
                </td>

                {/* Age */}
                <td className="px-3 py-3 text-right text-muted-foreground whitespace-nowrap">
                  {formatAge(result.publishDate)}
                </td>

                {/* Grab */}
                <td className="px-3 py-3 text-right">
                  <GrabButton result={result} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default SearchResults;
