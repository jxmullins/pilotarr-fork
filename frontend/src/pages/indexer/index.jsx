import React, { useState, useEffect } from "react";
import Header from "../../components/navigation/Header";
import Icon from "../../components/AppIcon";
import IndexerCard from "./components/IndexerCard";
import SearchBar from "./components/SearchBar";
import SearchResults from "./components/SearchResults";
import SearchHistory from "./components/SearchHistory";
import { getIndexers, getHistory, searchIndexers } from "../../services/prowlarrService";

const Indexer = () => {
  const [indexers, setIndexers] = useState([]);
  const [history, setHistory] = useState([]);
  const [searchResults, setSearchResults] = useState(null); // null = no search performed yet
  const [searchQuery, setSearchQuery] = useState("");
  const [loadingIndexers, setLoadingIndexers] = useState(true);
  const [loadingSearch, setLoadingSearch] = useState(false);
  const [historyOpen, setHistoryOpen] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setLoadingIndexers(true);
      const [idxData, histData] = await Promise.all([getIndexers(), getHistory(15)]);
      setIndexers(idxData);
      setHistory(histData);
      setLoadingIndexers(false);
    };
    fetchData();
  }, []);

  const handleSearch = async (query, type) => {
    setLoadingSearch(true);
    setSearchQuery(query);
    const results = await searchIndexers(query, type);
    setSearchResults(results);
    setLoadingSearch(false);
    // Scroll to results
    setTimeout(() => {
      document
        .getElementById("search-results")
        ?.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 100);
  };

  const handleIndexerToggle = (id, newState) => {
    setIndexers((prev) => prev.map((idx) => (idx.id === id ? { ...idx, enable: newState } : idx)));
  };

  // Stats summary
  const totalIndexers = indexers.length;
  const activeIndexers = indexers.filter((i) => i.enable).length;
  const totalQueries = indexers.reduce((acc, i) => acc + i.stats.numberOfQueries, 0);
  const totalGrabs = indexers.reduce((acc, i) => acc + i.stats.numberOfGrabs, 0);

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <div className="container mx-auto px-4 pt-20 md:pt-24 pb-8">
        {/* ── Page Header ── */}
        <div className="mb-6 md:mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
              <Icon name="Rss" size={20} color="var(--color-primary)" />
            </div>
            <div>
              <h1 className="text-2xl md:text-3xl font-bold text-foreground">Indexers</h1>
              <p className="text-sm text-muted-foreground">
                Manage Prowlarr indexers, search releases and view history
              </p>
            </div>
          </div>
        </div>

        {/* ── Stats Row ── */}
        {!loadingIndexers && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
            {[
              {
                label: "Total indexers",
                value: totalIndexers,
                icon: "Database",
                color: "text-primary",
              },
              {
                label: "Active",
                value: activeIndexers,
                icon: "CheckCircle",
                color: "text-emerald-400",
              },
              {
                label: "Disabled",
                value: totalIndexers - activeIndexers,
                icon: "PauseCircle",
                color: "text-slate-400",
              },
              {
                label: "Total queries",
                value: totalQueries.toLocaleString(),
                icon: "Activity",
                color: "text-amber-400",
              },
            ].map(({ label, value, icon, color }) => (
              <div
                key={label}
                className="bg-card border border-border rounded-lg p-3 flex items-center gap-3"
              >
                <Icon name={icon} size={18} className={color} />
                <div>
                  <p className="text-xs text-muted-foreground">{label}</p>
                  <p className={`text-lg font-bold ${color}`}>{value}</p>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* ── Indexers Grid ── */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-base font-semibold text-foreground flex items-center gap-2">
              <Icon name="Database" size={16} className="text-muted-foreground" />
              Configured Indexers
            </h2>
            <span className="text-xs text-muted-foreground">
              {activeIndexers}/{totalIndexers} active
            </span>
          </div>

          {loadingIndexers ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {[...Array(6)].map((_, i) => (
                <div
                  key={i}
                  className="bg-card border border-border rounded-lg p-4 animate-pulse h-40"
                />
              ))}
            </div>
          ) : indexers.length === 0 ? (
            <div className="bg-card border border-border rounded-lg p-8 text-center">
              <Icon name="Database" size={32} className="text-muted-foreground mx-auto mb-2" />
              <p className="text-muted-foreground">No indexers configured in Prowlarr</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {indexers.map((indexer) => (
                <IndexerCard key={indexer.id} indexer={indexer} onToggle={handleIndexerToggle} />
              ))}
            </div>
          )}
        </div>

        {/* ── Search Section ── */}
        <div className="mb-8">
          <div className="flex items-center gap-2 mb-3">
            <Icon name="Search" size={16} className="text-muted-foreground" />
            <h2 className="text-base font-semibold text-foreground">Search</h2>
          </div>

          <div className="bg-card border border-border rounded-lg p-4 mb-4">
            <SearchBar onSearch={handleSearch} loading={loadingSearch} />
          </div>

          {/* Results */}
          <div id="search-results">
            {loadingSearch && (
              <div className="bg-card border border-border rounded-lg p-8 text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-3" />
                <p className="text-muted-foreground text-sm">Querying indexers…</p>
              </div>
            )}

            {!loadingSearch && searchResults === null && (
              <div className="bg-card border border-dashed border-border rounded-lg p-8 text-center">
                <Icon name="Search" size={28} className="text-muted-foreground mx-auto mb-2" />
                <p className="text-muted-foreground text-sm">
                  Enter a query to search across all active indexers
                </p>
              </div>
            )}

            {!loadingSearch && searchResults !== null && searchResults.length === 0 && (
              <div className="bg-card border border-border rounded-lg p-8 text-center">
                <Icon name="SearchX" size={28} className="text-muted-foreground mx-auto mb-2" />
                <p className="text-foreground font-medium mb-1">No results found</p>
                <p className="text-muted-foreground text-sm">
                  Try a different query or check your indexers
                </p>
              </div>
            )}

            {!loadingSearch && searchResults !== null && searchResults.length > 0 && (
              <SearchResults results={searchResults} query={searchQuery} />
            )}
          </div>
        </div>

        {/* ── History Section ── */}
        <div>
          <button
            className="flex items-center gap-2 mb-3 w-full text-left group"
            onClick={() => setHistoryOpen((o) => !o)}
          >
            <Icon name="History" size={16} className="text-muted-foreground" />
            <h2 className="text-base font-semibold text-foreground group-hover:text-primary transition-colors">
              Recent History
            </h2>
            <span className="text-xs text-muted-foreground ml-1">({history.length})</span>
            <Icon
              name="ChevronDown"
              size={16}
              className={`ml-auto text-muted-foreground transition-transform ${historyOpen ? "" : "-rotate-90"}`}
            />
          </button>

          {historyOpen && (
            <div className="bg-card border border-border rounded-lg overflow-hidden">
              <SearchHistory history={history} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Indexer;
