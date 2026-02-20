from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app.api.schemas import SyncMetadataResponse
from app.db import SessionLocal, get_db
from app.models import SyncMetadata
from app.schedulers.sync_service import SyncService
from app.services.jellyfin_streams_service import JellyfinStreamsService

router = APIRouter(prefix="/sync", tags=["Synchronization"])


@router.post("/trigger")
async def trigger_sync(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Déclencher manuellement une synchronisation complète"""

    async def run_sync():
        sync_service = SyncService(db)
        await sync_service.sync_all()

    background_tasks.add_task(run_sync)

    return {"message": "Synchronisation lancée en arrière-plan", "status": "started"}


@router.post("/trigger/sonarr-episodes")
async def trigger_sonarr_episodes_sync(
    background_tasks: BackgroundTasks,
    full_sync: bool = False,
    series_limit: int = 5,
):
    """Déclencher la synchronisation des épisodes Sonarr"""

    async def run_episodes_sync():
        from app.db import SessionLocal

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


@router.post("/trigger/relink-sessions")
async def trigger_relink_sessions(background_tasks: BackgroundTasks):
    """Re-link PlaybackSessions with NULL library_item_id using improved matching."""

    async def run_relink():
        from sqlalchemy import func

        from app.db import SessionLocal
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
                    # Case-insensitive title + year
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
                        # Year-relaxed fallback
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
async def trigger_service_sync(service_name: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Déclencher la synchronisation d'un service spécifique"""

    async def run_service_sync():
        sync_service = SyncService(db)

        if service_name == "radarr":
            await sync_service.sync_radarr()
        elif service_name == "sonarr":
            await sync_service.sync_sonarr()
        elif service_name == "jellyfin":
            await sync_service.sync_jellyfin()
        elif service_name == "jellyseerr":
            await sync_service.sync_jellyseerr()

    background_tasks.add_task(run_service_sync)

    return {"message": f"Synchronisation {service_name} lancée", "status": "started"}


@router.get("/status", response_model=list[SyncMetadataResponse])
async def get_sync_status(db: Session = Depends(get_db)):
    """Récupérer le statut des dernières synchronisations"""
    sync_metadata = db.query(SyncMetadata).all()
    return sync_metadata
