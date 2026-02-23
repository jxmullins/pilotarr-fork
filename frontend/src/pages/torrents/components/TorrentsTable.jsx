import React, { useState } from "react";
import Icon from "../../../components/AppIcon";
import Button from "../../../components/ui/Button";

// ─── Formatters ─────────────────────────────────────────────────────────────

function formatBytes(bytes, decimals = 1) {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB", "TB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(decimals))} ${sizes[i]}`;
}

function formatSpeed(bytesPerSec) {
  if (bytesPerSec === 0) return <span className="text-muted-foreground">—</span>;
  return `${formatBytes(bytesPerSec)}/s`;
}

function formatEta(seconds) {
  if (seconds < 0) return <span className="text-muted-foreground">∞</span>;
  if (seconds === 0) return <span className="text-muted-foreground">—</span>;
  if (seconds < 60) return `${seconds}s`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${seconds % 60}s`;
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  return `${h}h ${m}m`;
}

function formatRatio(ratio) {
  const val = ratio.toFixed(2);
  let colorClass = "text-muted-foreground";
  if (ratio >= 1.0) colorClass = "text-success";
  else if (ratio >= 0.5) colorClass = "text-warning";
  else if (ratio > 0) colorClass = "text-error";
  return <span className={colorClass}>{val}</span>;
}

// ─── Status Badge ────────────────────────────────────────────────────────────

const STATUS_CONFIG = {
  downloading: {
    label: "Downloading",
    icon: "Download",
    className: "bg-primary/15 text-primary border-primary/30",
  },
  seeding: {
    label: "Seeding",
    icon: "Upload",
    className: "bg-success/15 text-success border-success/30",
  },
  paused: {
    label: "Paused",
    icon: "Pause",
    className: "bg-muted/60 text-muted-foreground border-border",
  },
  checking: {
    label: "Checking",
    icon: "RefreshCw",
    className: "bg-warning/15 text-warning border-warning/30",
  },
  error: {
    label: "Error",
    icon: "AlertCircle",
    className: "bg-error/15 text-error border-error/30",
  },
  queued: {
    label: "Queued",
    icon: "Clock",
    className: "bg-secondary/15 text-secondary border-secondary/30",
  },
};

function StatusBadge({ status }) {
  const cfg = STATUS_CONFIG[status] || STATUS_CONFIG.paused;
  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded border text-xs font-medium whitespace-nowrap ${cfg.className}`}
    >
      <Icon name={cfg.icon} size={11} className={status === "checking" ? "animate-spin" : ""} />
      {cfg.label}
    </span>
  );
}

// ─── Progress Bar ────────────────────────────────────────────────────────────

function ProgressBar({ progress, status }) {
  const pct = Math.round(progress * 100);
  let barColor = "bg-primary";
  if (status === "seeding") barColor = "bg-success";
  else if (status === "error") barColor = "bg-error";
  else if (status === "checking") barColor = "bg-warning";
  else if (status === "paused") barColor = "bg-muted-foreground";

  return (
    <div className="flex items-center gap-2 min-w-[80px]">
      <div className="flex-1 h-1.5 bg-muted rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all ${barColor}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="text-xs text-muted-foreground w-8 text-right tabular-nums">{pct}%</span>
    </div>
  );
}

// ─── Row Actions ─────────────────────────────────────────────────────────────

function RowActions({ torrent, onPauseResume, onRecheck }) {
  const isPaused = torrent.status === "paused";
  const isActive = ["downloading", "seeding"].includes(torrent.status);
  const canToggle = isPaused || isActive;

  return (
    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
      {canToggle && (
        <button
          onClick={(e) => {
            e.stopPropagation();
            onPauseResume(torrent);
          }}
          title={isPaused ? "Resume" : "Pause"}
          className="p-1.5 rounded hover:bg-muted text-muted-foreground hover:text-foreground transition-colors"
        >
          <Icon name={isPaused ? "Play" : "Pause"} size={13} />
        </button>
      )}
      <button
        onClick={(e) => {
          e.stopPropagation();
          onRecheck(torrent);
        }}
        title="Force recheck"
        className="p-1.5 rounded hover:bg-muted text-muted-foreground hover:text-foreground transition-colors"
      >
        <Icon name="RefreshCw" size={13} />
      </button>
    </div>
  );
}

// ─── Table ───────────────────────────────────────────────────────────────────

const COLUMNS = [
  { key: "name", label: "Name", sortable: true },
  { key: "status", label: "Status", sortable: true },
  { key: "size", label: "Size", sortable: true },
  { key: "progress", label: "Progress", sortable: true },
  { key: "dlSpeed", label: "↓ DL", sortable: true },
  { key: "ulSpeed", label: "↑ UL", sortable: true },
  { key: "seeds", label: "Seeds", sortable: true },
  { key: "peers", label: "Peers", sortable: true },
  { key: "ratio", label: "Ratio", sortable: true },
  { key: "eta", label: "ETA", sortable: true },
  { key: "tracker", label: "Tracker", sortable: true },
  { key: "addedOn", label: "Added", sortable: true },
  { key: "actions", label: "", sortable: false },
];

function SortIcon({ column, sortKey, sortDir }) {
  if (column !== sortKey) {
    return <Icon name="ChevronsUpDown" size={12} className="text-muted-foreground/40 ml-1" />;
  }
  return (
    <Icon
      name={sortDir === "asc" ? "ChevronUp" : "ChevronDown"}
      size={12}
      className="text-primary ml-1"
    />
  );
}

export default function TorrentsTable({
  data,
  selectedItems,
  onSelectAll,
  onSelectItem,
  onPauseResume,
  onRecheck,
}) {
  const [sortKey, setSortKey] = useState("addedOn");
  const [sortDir, setSortDir] = useState("desc");

  const handleSort = (key) => {
    if (!COLUMNS.find((c) => c.key === key)?.sortable) return;
    if (sortKey === key) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir("asc");
    }
  };

  const sorted = [...data].sort((a, b) => {
    let aVal = a[sortKey];
    let bVal = b[sortKey];
    // Nulls always last
    if (aVal == null && bVal == null) return 0;
    if (aVal == null) return 1;
    if (bVal == null) return -1;
    if (typeof aVal === "string") aVal = aVal.toLowerCase();
    if (typeof bVal === "string") bVal = bVal.toLowerCase();
    if (aVal < bVal) return sortDir === "asc" ? -1 : 1;
    if (aVal > bVal) return sortDir === "asc" ? 1 : -1;
    return 0;
  });

  const allSelected = data.length > 0 && selectedItems.length === data.length;
  const someSelected = selectedItems.length > 0 && selectedItems.length < data.length;

  if (data.length === 0) {
    return (
      <div className="bg-card border border-border rounded-lg flex flex-col items-center justify-center py-16 text-center">
        <Icon name="Download" size={40} className="text-muted-foreground/30 mb-3" />
        <p className="text-muted-foreground font-medium">No torrents found</p>
        <p className="text-sm text-muted-foreground/60 mt-1">
          No torrents match the current filter
        </p>
      </div>
    );
  }

  return (
    <div className="bg-card border border-border rounded-lg overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-sm min-w-[900px]">
          {/* Header */}
          <thead>
            <tr className="border-b border-border bg-muted/30">
              <th className="px-3 py-2.5 w-8">
                <input
                  type="checkbox"
                  checked={allSelected}
                  ref={(el) => {
                    if (el) el.indeterminate = someSelected;
                  }}
                  onChange={(e) => onSelectAll(e.target.checked)}
                  className="rounded border-border accent-primary cursor-pointer"
                />
              </th>
              {COLUMNS.map((col) => (
                <th
                  key={col.key}
                  onClick={() => handleSort(col.key)}
                  className={`px-3 py-2.5 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider whitespace-nowrap
                    ${col.sortable ? "cursor-pointer hover:text-foreground select-none" : ""}`}
                >
                  <span className="inline-flex items-center">
                    {col.label}
                    {col.sortable && (
                      <SortIcon column={col.key} sortKey={sortKey} sortDir={sortDir} />
                    )}
                  </span>
                </th>
              ))}
            </tr>
          </thead>

          {/* Body */}
          <tbody className="divide-y divide-border/50">
            {sorted.map((torrent) => {
              const isSelected = selectedItems.includes(torrent.id);
              return (
                <tr
                  key={torrent.id}
                  className={`group transition-colors
                    ${isSelected ? "bg-primary/5" : "hover:bg-muted/20"}`}
                >
                  {/* Checkbox */}
                  <td className="px-3 py-2.5">
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={(e) => onSelectItem(torrent.id, e.target.checked)}
                      className="rounded border-border accent-primary cursor-pointer"
                    />
                  </td>

                  {/* Name */}
                  <td className="px-3 py-2.5 max-w-[280px]">
                    <div className="flex flex-col gap-0.5">
                      <span
                        className="font-medium text-foreground truncate block"
                        title={torrent.name}
                      >
                        {torrent.name}
                      </span>
                      <div className="flex items-center gap-2">
                        {torrent.category && (
                          <span className="text-xs text-muted-foreground/70 bg-muted/50 px-1.5 py-0.5 rounded">
                            {torrent.category}
                          </span>
                        )}
                        {torrent.tags?.map((tag) => (
                          <span
                            key={tag}
                            className="text-xs text-accent/80 bg-accent/10 px-1.5 py-0.5 rounded"
                          >
                            {tag}
                          </span>
                        ))}
                        {torrent.errorMessage && (
                          <span className="text-xs text-error/80" title={torrent.errorMessage}>
                            {torrent.errorMessage}
                          </span>
                        )}
                      </div>
                    </div>
                  </td>

                  {/* Status */}
                  <td className="px-3 py-2.5">
                    <StatusBadge status={torrent.status} />
                  </td>

                  {/* Size */}
                  <td className="px-3 py-2.5 text-muted-foreground tabular-nums whitespace-nowrap">
                    {formatBytes(torrent.size)}
                  </td>

                  {/* Progress */}
                  <td className="px-3 py-2.5">
                    <ProgressBar progress={torrent.progress} status={torrent.status} />
                  </td>

                  {/* DL Speed */}
                  <td className="px-3 py-2.5 tabular-nums text-primary whitespace-nowrap font-medium">
                    {formatSpeed(torrent.dlSpeed)}
                  </td>

                  {/* UL Speed */}
                  <td className="px-3 py-2.5 tabular-nums text-success whitespace-nowrap font-medium">
                    {formatSpeed(torrent.ulSpeed)}
                  </td>

                  {/* Seeds */}
                  <td className="px-3 py-2.5 text-muted-foreground tabular-nums">
                    {torrent.seeds > 0 ? (
                      <span className="text-success">{torrent.seeds}</span>
                    ) : (
                      <span className="text-muted-foreground/50">0</span>
                    )}
                  </td>

                  {/* Peers */}
                  <td className="px-3 py-2.5 text-muted-foreground tabular-nums">
                    {torrent.peers > 0 ? (
                      torrent.peers
                    ) : (
                      <span className="text-muted-foreground/50">0</span>
                    )}
                  </td>

                  {/* Ratio */}
                  <td className="px-3 py-2.5 tabular-nums font-medium">
                    {formatRatio(torrent.ratio)}
                  </td>

                  {/* ETA */}
                  <td className="px-3 py-2.5 text-muted-foreground tabular-nums whitespace-nowrap">
                    {formatEta(torrent.eta)}
                  </td>

                  {/* Tracker */}
                  <td className="px-3 py-2.5 text-muted-foreground text-xs max-w-[140px]">
                    <span className="truncate block" title={torrent.tracker}>
                      {torrent.tracker}
                    </span>
                  </td>

                  {/* Added On */}
                  <td className="px-3 py-2.5 text-sm text-muted-foreground whitespace-nowrap">
                    {torrent.addedOn
                      ? new Date(torrent.addedOn).toLocaleDateString(undefined, {
                          year: "numeric",
                          month: "short",
                          day: "numeric",
                        })
                      : "—"}
                  </td>

                  {/* Actions */}
                  <td className="px-3 py-2.5">
                    <RowActions
                      torrent={torrent}
                      onPauseResume={onPauseResume}
                      onRecheck={onRecheck}
                    />
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Footer */}
      <div className="border-t border-border px-4 py-2.5 flex items-center justify-between bg-muted/10">
        <span className="text-xs text-muted-foreground">
          {data.length} torrent{data.length !== 1 ? "s" : ""}
          {selectedItems.length > 0 && (
            <span className="text-primary ml-2">· {selectedItems.length} selected</span>
          )}
        </span>
        <span className="text-xs text-muted-foreground">qBittorrent</span>
      </div>
    </div>
  );
}
