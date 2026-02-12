from datetime import UTC, datetime, timedelta
from typing import Any

from app.services.base_connector import BaseConnector


class SonarrConnector(BaseConnector):
    """Connecteur pour l'API Sonarr"""

    def _get_headers(self) -> dict[str, str]:
        """Headers spécifiques à Sonarr"""
        return {**super()._get_headers(), "X-Api-Key": self.api_key}

    async def test_connection(self) -> tuple[bool, str]:
        """Tester la connexion à Sonarr"""
        try:
            response = await self._get("/api/v3/system/status")
            version = response.get("version", "unknown")
            return True, f"Connecté à Sonarr v{version}"
        except Exception as e:
            return False, f"Erreur de connexion: {str(e)}"

    async def get_series(self) -> list[dict[str, Any]]:
        """
        Récupérer toutes les séries

        Returns:
            Liste des séries avec leurs détails
        """
        try:
            series = await self._get("/api/v3/series")
            return series
        except Exception as e:
            print(f"❌ Erreur récupération séries Sonarr: {e}")
            return []

    async def get_calendar(self, days_ahead: int = 30) -> list[dict[str, Any]]:
        """
        Récupérer le calendrier des épisodes à venir

        Args:
            days_ahead: Nombre de jours à venir

        Returns:
            Liste des épisodes à venir
        """
        try:
            start_date = datetime.now(UTC).date()
            end_date = start_date + timedelta(days=days_ahead)

            params = {"start": start_date.isoformat(), "end": end_date.isoformat(), "includeSeries": "true"}

            calendar = await self._get("/api/v3/calendar", params=params)
            return calendar
        except Exception as e:
            print(f"❌ Erreur récupération calendrier Sonarr: {e}")
            return []

    async def get_recent_additions(self, days: int = 7) -> list[dict[str, Any]]:
        """
        Récupérer les séries récemment ajoutées

        Args:
            days: Nombre de jours en arrière

        Returns:
            Liste des séries récemment ajoutées
        """
        try:
            series = await self.get_series()

            # Filtrer par date d'ajout
            cutoff_date = datetime.now(UTC) - timedelta(days=days)

            recent = []
            for serie in series:
                if not serie.get("added"):
                    continue

                try:
                    # Convertir la date en timezone-aware
                    added_dt = datetime.fromisoformat(serie["added"].replace("Z", "+00:00"))
                    if added_dt > cutoff_date:
                        recent.append(serie)
                except (ValueError, AttributeError):
                    # Ignorer les films avec des dates invalides
                    continue

            # Trier par date d'ajout
            recent.sort(key=lambda x: x.get("added", ""), reverse=True)
            return recent

        except Exception as e:
            print(f"❌ Erreur récupération séries récentes: {e}")
            return []

    async def get_history(self, page_size: int = 50) -> list[dict[str, Any]]:
        """
        Récupérer l'historique des téléchargements

        Args:
            page_size: Nombre d'enregistrements à récupérer

        Returns:
            Liste des événements d'historique avec downloadId
        """
        try:
            params = {
                "pageSize": page_size,
                "sortKey": "date",
                "sortDirection": "descending",
                "eventType": 3,  # 3 = Downloaded for Sonarr
            }

            response = await self._get("/api/v3/history", params=params)
            records = response.get("records", [])

            return records

        except Exception as e:
            print(f"❌ Erreur récupération historique Sonarr: {e}")
            return []

    async def get_series_history_map(self) -> dict[int, str]:
        """
        Créer une map {seriesId: torrent_hash} (backward compat, returns first hash only)

        Returns:
            Dictionnaire associant les IDs de séries aux hash de torrents
        """
        torrents_map = await self.get_series_torrents_map()
        return {series_id: entries[0]["hash"] for series_id, entries in torrents_map.items() if entries}

    async def get_series_torrents_map(self) -> dict[int, list[dict]]:
        """
        Créer une map {seriesId: [{hash, episode_id, season_number, is_season_pack}, ...]}

        Fetches history with a larger page size to capture all torrents per series.
        Detects season packs by finding hashes shared across multiple episodes.

        Returns:
            Dict mapping series IDs to lists of torrent info dicts
        """
        history = await self.get_history(page_size=500)

        # First pass: collect all (hash, episode, season) tuples per series
        # Also track which episodes each hash covers (for season pack detection)
        series_entries: dict[int, dict[str, dict]] = {}  # {seriesId: {hash: entry_dict}}
        hash_episodes: dict[str, set[int]] = {}  # {hash: {episodeId, ...}}

        for record in history:
            series_id = record.get("seriesId")
            download_id = record.get("downloadId", "")
            episode_id = record.get("episodeId")
            season_number = record.get("seasonNumber")

            if not series_id or not download_id:
                continue

            hash_value = self._extract_hash(download_id)
            if not hash_value:
                continue

            # Track episodes per hash for season pack detection
            if hash_value not in hash_episodes:
                hash_episodes[hash_value] = set()
            if episode_id:
                hash_episodes[hash_value].add(episode_id)

            # Store unique hash per series
            if series_id not in series_entries:
                series_entries[series_id] = {}

            if hash_value not in series_entries[series_id]:
                series_entries[series_id][hash_value] = {
                    "hash": hash_value,
                    "episode_id": episode_id,
                    "season_number": season_number,
                    "is_season_pack": False,
                }

        # Second pass: mark season packs (hash covers 2+ episodes)
        for series_id, entries in series_entries.items():
            for hash_value, entry in entries.items():
                if len(hash_episodes.get(hash_value, set())) > 1:
                    entry["is_season_pack"] = True
                    entry["episode_id"] = None  # Not tied to a single episode

        # Convert to list format
        return {series_id: list(entries.values()) for series_id, entries in series_entries.items()}

    def _extract_hash(self, download_id: str) -> str | None:
        """
        Extraire le hash du torrent depuis le downloadId

        Args:
            download_id: ID du téléchargement (ex: "qBittorrent-HASH" ou "HASH")

        Returns:
            Hash du torrent ou None
        """
        if not download_id:
            return None

        # Si format "qBittorrent-HASH"
        if "-" in download_id:
            parts = download_id.split("-", 1)
            if len(parts) == 2:
                return parts[1].upper()

        # Si c'est directement le hash (40 caractères hexadécimaux)
        if len(download_id) == 40 and all(c in "0123456789ABCDEFabcdef" for c in download_id):
            return download_id.upper()

        return None

    async def get_statistics(self) -> dict[str, Any]:
        """
        Récupérer les statistiques Sonarr

        Returns:
            Statistiques (séries, épisodes, etc.)
        """
        try:
            series = await self.get_series()

            total_series = len(series)
            monitored_series = sum(1 for s in series if s.get("monitored"))

            total_episodes = sum(s.get("statistics", {}).get("episodeCount", 0) for s in series)
            downloaded_episodes = sum(s.get("statistics", {}).get("episodeFileCount", 0) for s in series)
            missing_episodes = total_episodes - downloaded_episodes

            return {
                "total_series": total_series,
                "monitored_series": monitored_series,
                "total_episodes": total_episodes,
                "downloaded_episodes": downloaded_episodes,
                "missing_episodes": missing_episodes,
            }

        except Exception as e:
            print(f"❌ Erreur récupération stats Sonarr: {e}")
            return {}
