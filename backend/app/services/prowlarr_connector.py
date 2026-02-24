from typing import Any

from app.services.base_connector import BaseConnector


class ProwlarrConnector(BaseConnector):
    """Connector for the Prowlarr API"""

    def _get_headers(self) -> dict[str, str]:
        return {**super()._get_headers(), "X-Api-Key": self.api_key}

    async def test_connection(self) -> tuple[bool, str]:
        try:
            response = await self._get("/api/v1/system/status")
            version = response.get("version", "unknown")
            return True, f"Connected to Prowlarr v{version}"
        except Exception as e:
            return False, f"Connection error: {str(e)}"

    async def get_indexers(self) -> list[dict[str, Any]]:
        try:
            return await self._get("/api/v1/indexer")
        except Exception as e:
            print(f"❌ Prowlarr get_indexers error: {e}")
            return []

    async def get_indexer_stats(self) -> list[dict[str, Any]]:
        try:
            response = await self._get("/api/v1/indexerstats")
            return response.get("indexers", [])
        except Exception as e:
            print(f"❌ Prowlarr get_indexer_stats error: {e}")
            return []

    async def get_indexers_with_stats(self) -> list[dict[str, Any]]:
        """Return indexers enriched with their per-indexer stats."""
        indexers, stats_list = await self.get_indexers(), await self.get_indexer_stats()
        stats_map = {s["indexerId"]: s for s in stats_list}
        empty_stats = {
            "numberOfQueries": 0,
            "numberOfFailedQueries": 0,
            "numberOfGrabs": 0,
            "numberOfFailedGrabs": 0,
            "averageResponseTime": 0,
        }
        result = []
        for idx in indexers:
            raw_stats = stats_map.get(idx["id"], {})
            result.append(
                {
                    "id": idx["id"],
                    "name": idx["name"],
                    "enable": idx.get("enable", True),
                    "protocol": idx.get("protocol", "torrent"),
                    "privacy": idx.get("privacy", "public"),
                    "capabilities": {
                        "categories": [c.get("name", "") for c in idx.get("capabilities", {}).get("categories", [])]
                    },
                    "stats": {
                        "numberOfQueries": raw_stats.get("numberOfQueries", 0),
                        "numberOfFailedQueries": raw_stats.get("numberOfFailedQueries", 0),
                        "numberOfGrabs": raw_stats.get("numberOfGrabs", 0),
                        "numberOfFailedGrabs": raw_stats.get("numberOfFailedGrabs", 0),
                        "averageResponseTime": raw_stats.get("averageResponseTime", 0),
                    },
                }
                if raw_stats
                else {
                    "id": idx["id"],
                    "name": idx["name"],
                    "enable": idx.get("enable", True),
                    "protocol": idx.get("protocol", "torrent"),
                    "privacy": idx.get("privacy", "public"),
                    "capabilities": {
                        "categories": [c.get("name", "") for c in idx.get("capabilities", {}).get("categories", [])]
                    },
                    "stats": empty_stats,
                }
            )
        return result

    async def toggle_indexer(self, indexer_id: int, enable: bool) -> bool:
        """Enable or disable an indexer (GET config → mutate → PUT back)."""
        try:
            indexer = await self._get(f"/api/v1/indexer/{indexer_id}")
            indexer["enable"] = enable
            await self._put(f"/api/v1/indexer/{indexer_id}", indexer)
            return True
        except Exception as e:
            print(f"❌ Prowlarr toggle_indexer error: {e}")
            return False

    async def get_history(self, page_size: int = 15) -> list[dict[str, Any]]:
        try:
            # Build indexerId → name map from the indexers list
            indexers = await self.get_indexers()
            indexer_map = {idx["id"]: idx["name"] for idx in indexers}

            params = {"pageSize": page_size, "sortKey": "date", "sortDirection": "descending"}
            response = await self._get("/api/v1/history", params=params)
            records = response.get("records", [])
            result = []
            for r in records:
                data = r.get("data") or {}
                query = data.get("query") or ""
                categories = [s.strip() for s in str(data.get("categories", "")).split(",") if s.strip()]
                indexer_id = r.get("indexerId")
                result.append(
                    {
                        "id": r.get("id"),
                        "date": r.get("date"),
                        "indexer": indexer_map.get(indexer_id, f"#{indexer_id}") if indexer_id else "",
                        "query": query,
                        "categories": categories,
                        "eventType": r.get("eventType") or "",
                        "successful": r.get("successful", True),
                        "source": data.get("source") or "",
                    }
                )
            return result
        except Exception as e:
            print(f"❌ Prowlarr get_history error: {e}")
            return []

    async def search(self, query: str, search_type: str = "search") -> list[dict[str, Any]]:
        try:
            params = {"query": query, "type": search_type}
            results = await self._get("/api/v1/search", params=params)
            return [
                {
                    "guid": r.get("guid", ""),
                    "title": r.get("title", ""),
                    "indexer": r.get("indexer", ""),
                    "indexerId": r.get("indexerId"),
                    "size": r.get("size"),
                    "seeders": r.get("seeders"),
                    "leechers": r.get("leechers"),
                    "protocol": r.get("protocol", "torrent"),
                    "publishDate": r.get("publishDate"),
                    "categories": [c.get("name", "") for c in r.get("categories", [])],
                    "downloadUrl": r.get("downloadUrl"),
                    "magnetUrl": r.get("magnetUrl"),
                }
                for r in results
            ]
        except Exception as e:
            print(f"❌ Prowlarr search error: {e}")
            return []

    async def grab(self, guid: str, indexer_id: int) -> bool:
        try:
            await self._post("/api/v1/search", {"guid": guid, "indexerId": indexer_id})
            return True
        except Exception as e:
            print(f"❌ Prowlarr grab error: {e}")
            return False
