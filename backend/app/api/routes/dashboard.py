from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app.api.schemas import (
    CalendarEventResponse,
    DashboardStatisticResponse,
    JellyseerrRequestResponse,
    LibraryItemResponse,
)
from app.db import get_db
from app.models import CalendarEvent, DashboardStatistic, JellyseerrRequest, LibraryItem
from app.models.enums import ItemSortBy

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

TORRENT_INFO_ALLOWED_KEYS = {"seeding_time", "ratio", "size", "download_date", "status"}


def _build_torrent_info_array(item: LibraryItem) -> list[dict]:
    """Build torrent_info array from the torrents relationship, stripping unwanted keys."""
    result = []
    for t in item.torrents:
        if not t.torrent_info:
            continue
        result.append({k: v for k, v in t.torrent_info.items() if k in TORRENT_INFO_ALLOWED_KEYS})
    return result


@router.get("/statistics", response_model=list[DashboardStatisticResponse])
async def get_statistics(db: Session = Depends(get_db)):
    """Récupérer uniquement les statistiques"""
    statistics = db.query(DashboardStatistic).all()
    return statistics


@router.get("/recent-items", response_model=list[LibraryItemResponse])
async def get_recent_items(
    limit: int = Query(default=20, ge=1, le=100),
    sort_by: ItemSortBy = Query(default=ItemSortBy.ADDED_DATE),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
):
    """Récupérer les items récemment ajoutés"""
    # Sort still uses the pre-aggregated torrent_info JSON column for ratio
    sort_mapping = {
        ItemSortBy.ADDED_DATE: LibraryItem.created_at,
        ItemSortBy.TITLE: LibraryItem.title,
        ItemSortBy.SIZE: LibraryItem.size,
        ItemSortBy.RATIO: func.json_extract(LibraryItem.torrent_info, "$.ratio"),
    }

    sort_column = sort_mapping[sort_by]

    if sort_order == "asc":
        sort_clause = sort_column.asc()
    else:
        sort_clause = sort_column.desc()

    items = db.query(LibraryItem).options(selectinload(LibraryItem.torrents)).order_by(sort_clause).limit(limit).all()

    # Override torrent_info with array from relationship at serialization time
    results = []
    for item in items:
        data = {
            "id": item.id,
            "title": item.title,
            "year": item.year,
            "media_type": item.media_type,
            "image_url": item.image_url,
            "image_alt": item.image_alt,
            "quality": item.quality,
            "rating": item.rating,
            "description": item.description,
            "added_date": item.added_date,
            "size": item.size,
            "nb_media": item.nb_media,
            "created_at": item.created_at,
            "torrent_info": _build_torrent_info_array(item),
        }
        results.append(data)

    return results


@router.get("/calendar", response_model=list[CalendarEventResponse])
async def get_calendar(
    start: str | None = Query(default=None, description="Start date YYYY-MM-DD"),
    end: str | None = Query(default=None, description="End date YYYY-MM-DD"),
    db: Session = Depends(get_db),
):
    """Récupérer le calendrier des sorties (passé et futur)"""
    today = datetime.now().date()

    if start:
        try:
            start_date = datetime.strptime(start, "%Y-%m-%d").date()
        except ValueError:
            start_date = today - timedelta(days=30)
    else:
        start_date = today - timedelta(days=30)

    if end:
        try:
            end_date = datetime.strptime(end, "%Y-%m-%d").date()
        except ValueError:
            end_date = today + timedelta(days=30)
    else:
        end_date = today + timedelta(days=30)

    events = (
        db.query(CalendarEvent)
        .filter(CalendarEvent.release_date >= start_date)
        .filter(CalendarEvent.release_date <= end_date)
        .order_by(CalendarEvent.release_date.asc())
        .all()
    )

    return events


@router.get("/requests", response_model=list[JellyseerrRequestResponse])
async def get_requests(
    limit: int = Query(default=20, ge=1, le=100),
    status: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    """Récupérer les requêtes Jellyseerr"""
    from app.models.enums import RequestStatus

    _status_name_map = {
        "pending": RequestStatus.PENDING,
        "approved": RequestStatus.APPROVED,
        "declined": RequestStatus.DECLINED,
    }

    query = db.query(JellyseerrRequest)
    if status is not None and status != "all":
        status_enum = None
        if status in _status_name_map:
            status_enum = _status_name_map[status]
        else:
            try:
                status_enum = RequestStatus(int(status))
            except (ValueError, KeyError):
                return []
        query = query.filter(JellyseerrRequest.status == status_enum)
    return query.order_by(JellyseerrRequest.created_at.desc()).limit(limit).all()
