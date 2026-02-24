import React, { useState } from "react";
import Icon from "../../../components/AppIcon";

const SEARCH_TYPES = [
  { value: "search", label: "All" },
  { value: "moviesearch", label: "Movies" },
  { value: "tvsearch", label: "TV Shows" },
  { value: "audiobooksearch", label: "Music" },
];

const SearchBar = ({ onSearch, loading }) => {
  const [query, setQuery] = useState("");
  const [type, setType] = useState("search");

  const handleSubmit = (e) => {
    e.preventDefault();
    const q = query.trim();
    if (!q) return;
    onSearch(q, type);
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-2">
      {/* Category selector */}
      <div className="flex-shrink-0">
        <select
          value={type}
          onChange={(e) => setType(e.target.value)}
          className="h-10 px-3 rounded-lg bg-card border border-border text-foreground text-sm focus:outline-none focus:ring-1 focus:ring-primary cursor-pointer"
        >
          {SEARCH_TYPES.map((t) => (
            <option key={t.value} value={t.value}>
              {t.label}
            </option>
          ))}
        </select>
      </div>

      {/* Query input */}
      <div className="relative flex-1">
        <Icon
          name="Search"
          size={16}
          className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground pointer-events-none"
        />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search across all indexers…"
          className="w-full h-10 pl-9 pr-4 rounded-lg bg-card border border-border text-foreground placeholder:text-muted-foreground text-sm focus:outline-none focus:ring-1 focus:ring-primary"
        />
      </div>

      {/* Submit */}
      <button
        type="submit"
        disabled={!query.trim() || loading}
        className="h-10 px-5 rounded-lg bg-primary text-white text-sm font-medium flex items-center gap-2 hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex-shrink-0"
      >
        {loading ? (
          <>
            <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            Searching…
          </>
        ) : (
          <>
            <Icon name="Search" size={14} />
            Search
          </>
        )}
      </button>
    </form>
  );
};

export default SearchBar;
