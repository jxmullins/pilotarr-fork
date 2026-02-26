from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app.api.schemas import SyncMetadataResponse
from app.db import SessionLocal, get_db
from app.models import SyncMetadata
from app.schedulers.sync_service import SyncService
from app.services.jellyfin_streams_service import JellyfinStreamsService
from app.services.torrent_enrichment_service import TorrentEnrichmentService

router = APIRouter(prefix="/sync", tags=["Synchronization"])


@router.post("/trigger")
async def trigger_sync(background_tasks: BackgroundTasks):
    """Déclencher manuellement une synchronisation complète (identique au scheduler)"""

    async def run_sync():
        db = SessionLocal()
        try:
            sync_service = SyncService(db)

            # 1. All core services
            await sync_service.sync_all()

            # 2. Torrent enrichment from qBittorrent
            torrent_service = TorrentEnrichmentService(db)
            stats = await torrent_service.enrich_all_items(limit=50)
            print(f"✅ Torrents enrichis : {stats.get('success')}/{stats.get('total')}")

            # 3. Sonarr episodes (all series, batched)
            await sync_service.sync_sonarr_episodes(full_sync=True, batch_size=20)

            # 4. Jellyfin MediaStreams (subtitles, audio tracks)
            streams_service = JellyfinStreamsService(db)
            await streams_service.sync_all()

        except Exception as e:
            import traceback

            print(f"❌ Erreur lors de la synchro manuelle: {e}")
            traceback.print_exc()
        finally:
            db.close()

    background_tasks.add_task(run_sync)
    return {"message": "Synchronisation complète lancée en arrière-plan", "status": "started"}


@router.post("/trigger/sonarr-episodes")
async def trigger_sonarr_episodes_sync(
    background_tasks: BackgroundTasks,
    full_sync: bool = False,
    series_limit: int = 5,
):
    """Déclencher la synchronisation des épisodes Sonarr"""

    async def run_episodes_sync():
        db = SessionLocal()
        try:
            print("=" * 80)
            print("🚀 EPISODES SYNC STARTED (Background)")
            print(f"🚀 Parameters: full_sync={full_sync}, series_limit={series_limit}")
            print("=" * 80)

            sync_service = SyncService(db)
            result = await sync_service.sync_sonarr_episodes(full_sync=full_sync, series_limit=series_limit)
            print(f"📊 Episodes sync completed: {result}")
        except Exception as e:
            print(f"❌ Error in episodes sync: {e}")
            import traceback

            traceback.print_exc()
        finally:
            db.close()

    background_tasks.add_task(run_episodes_sync)

    return {
        "message": f"Synchronisation épisodes lancée (full_sync={full_sync}, limit={series_limit})",
        "status": "started",
    }


@router.post("/trigger/sonarr-seasons")
async def trigger_sonarr_seasons_sync(background_tasks: BackgroundTasks):
    """Déclencher la synchronisation des saisons Sonarr"""

    async def run_seasons_sync():
        db = SessionLocal()
        try:
            sync_service = SyncService(db)
            result = await sync_service.sync_sonarr_seasons()
            print(f"📊 Seasons sync completed: {result}")
        except Exception as e:
            print(f"❌ Error in seasons sync: {e}")
        finally:
            db.close()

    background_tasks.add_task(run_seasons_sync)
    return {"message": "Synchronisation saisons Sonarr lancée en arrière-plan", "status": "started"}


@router.post("/trigger/jellyfin-streams")
async def trigger_jellyfin_streams_sync(background_tasks: BackgroundTasks):
    """Déclencher la synchronisation des MediaStreams Jellyfin (sous-titres, audio)"""

    async def run_streams_sync():
        db = SessionLocal()
        try:
            service = JellyfinStreamsService(db)
            result = await service.sync_all()
            print(f"📊 Streams sync completed: {result}")
        except Exception as e:
            print(f"❌ Error in streams sync: {e}")
        finally:
            db.close()

    background_tasks.add_task(run_streams_sync)
    return {"message": "Synchronisation MediaStreams Jellyfin lancée en arrière-plan", "status": "started"}


@router.post("/trigger/torrents")
async def trigger_torrents_sync(background_tasks: BackgroundTasks, limit: int = 50):
    """Déclencher l'enrichissement des torrents depuis qBittorrent"""

    async def run_torrents_sync():
        db = SessionLocal()
        try:
            service = TorrentEnrichmentService(db)
            result = await service.enrich_all_items(limit=limit)
            print(f"📊 Torrent enrichment completed: {result}")
        except Exception as e:
            print(f"❌ Error in torrent enrichment: {e}")
        finally:
            db.close()

    background_tasks.add_task(run_torrents_sync)
    return {"message": f"Enrichissement torrents lancé (limit={limit})", "status": "started"}


@router.post("/trigger/monitored-items")
async def trigger_monitored_items_sync(background_tasks: BackgroundTasks):
    """Déclencher la synchronisation des items monitorés (Radarr + Sonarr stats)"""

    async def run_monitored_sync():
        db = SessionLocal()
        try:
            sync_service = SyncService(db)
            result = await sync_service.sync_monitored_items()
            print(f"📊 Monitored items sync completed: {result}")
        except Exception as e:
            print(f"❌ Error in monitored items sync: {e}")
        finally:
            db.close()

    background_tasks.add_task(run_monitored_sync)
    return {"message": "Synchronisation items monitorés lancée en arrière-plan", "status": "started"}


@router.post("/trigger/relink-sessions")
async def trigger_relink_sessions(background_tasks: BackgroundTasks):
    """Re-link PlaybackSessions with NULL library_item_id using improved matching."""

    async def run_relink():
        from sqlalchemy import func

        from app.models.enums import MediaType
        from app.models.models import LibraryItem, PlaybackSession

        db = SessionLocal()
        try:
            print("🔗 Starting session re-linking...")
            unlinked = db.query(PlaybackSession).filter(PlaybackSession.library_item_id.is_(None)).all()
            print(f"   → {len(unlinked)} unlinked sessions found")

            linked = 0
            for session in unlinked:
                library_item = None
                media_type_str = session.media_type.value if session.media_type else None

                if media_type_str == "movie":
                    library_item = (
                        db.query(LibraryItem)
                        .filter(
                            func.lower(LibraryItem.title) == session.media_title.lower(),
                            LibraryItem.media_type == MediaType.MOVIE,
                            LibraryItem.year == session.media_year,
                        )
                        .first()
                    )
                    if not library_item:
                        library_item = (
                            db.query(LibraryItem)
                            .filter(
                                func.lower(LibraryItem.title) == session.media_title.lower(),
                                LibraryItem.media_type == MediaType.MOVIE,
                            )
                            .first()
                        )
                elif media_type_str == "tv":
                    library_item = (
                        db.query(LibraryItem)
                        .filter(
                            func.lower(LibraryItem.title) == session.media_title.lower(),
                            LibraryItem.media_type == MediaType.TV,
                        )
                        .first()
                    )

                if library_item:
                    session.library_item_id = library_item.id
                    linked += 1

            db.commit()
            print(f"✅ Re-linking complete: {linked}/{len(unlinked)} sessions linked")
        except Exception as e:
            db.rollback()
            print(f"❌ Error during re-linking: {e}")
            import traceback

            traceback.print_exc()
        finally:
            db.close()

    background_tasks.add_task(run_relink)
    return {"message": "Session re-linking started in background", "status": "started"}


@router.post("/trigger/{service_name}")
async def trigger_service_sync(service_name: str, background_tasks: BackgroundTasks):
    """Déclencher la synchronisation d'un service spécifique"""

    valid_services = {
        "radarr",
        "sonarr",
        "jellyfin",
        "jellyseerr",
        "qbittorrent",
        "monitored-items",
        "sonarr-seasons",
    }
    if service_name not in valid_services:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail=f"Service '{service_name}' non reconnu")

    async def run_service_sync():
        db = SessionLocal()
        try:
            sync_service = SyncService(db)

            if service_name == "radarr":
                await sync_service.sync_radarr()
            elif service_name == "sonarr":
                await sync_service.sync_sonarr()
            elif service_name == "jellyfin":
                await sync_service.sync_jellyfin()
            elif service_name == "jellyseerr":
                await sync_service.sync_jellyseerr()
            elif service_name == "monitored-items":
                await sync_service.sync_monitored_items()
            elif service_name == "sonarr-seasons":
                await sync_service.sync_sonarr_seasons()
            elif service_name == "qbittorrent":
                torrent_service = TorrentEnrichmentService(db)
                await torrent_service.enrich_all_items(limit=50)
        except Exception as e:
            print(f"❌ Error in {service_name} sync: {e}")
        finally:
            db.close()

    background_tasks.add_task(run_service_sync)
    return {"message": f"Synchronisation {service_name} lancée", "status": "started"}


@router.get("/status", response_model=list[SyncMetadataResponse])
async def get_sync_status(db: Session = Depends(get_db)):
    """Récupérer le statut des dernières synchronisations"""
    sync_metadata = db.query(SyncMetadata).all()
    return sync_metadata
