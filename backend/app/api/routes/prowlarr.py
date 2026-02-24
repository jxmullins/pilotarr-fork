from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.schemas import (
    ProwlarrGrabRequest,
    ProwlarrHistoryItem,
    ProwlarrIndexerResponse,
    ProwlarrIndexerToggle,
    ProwlarrSearchResult,
)
from app.db import get_db
from app.models import ServiceConfiguration, ServiceType
from app.services.prowlarr_connector import ProwlarrConnector

router = APIRouter(prefix="/prowlarr", tags=["Prowlarr"])


def _get_connector(db: Session) -> ProwlarrConnector:
    service = db.query(ServiceConfiguration).filter(ServiceConfiguration.service_name == ServiceType.PROWLARR).first()
    if not service or not service.is_active:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Prowlarr is not configured or inactive",
        )
    return ProwlarrConnector(base_url=service.url, api_key=service.api_key, port=service.port)


@router.get("/indexers", response_model=list[ProwlarrIndexerResponse])
async def get_indexers(db: Session = Depends(get_db)):
    """Return all indexers with their stats."""
    connector = _get_connector(db)
    try:
        return await connector.get_indexers_with_stats()
    finally:
        await connector.close()


@router.patch("/indexers/{indexer_id}")
async def toggle_indexer(indexer_id: int, body: ProwlarrIndexerToggle, db: Session = Depends(get_db)):
    """Enable or disable an indexer."""
    connector = _get_connector(db)
    try:
        ok = await connector.toggle_indexer(indexer_id, body.enable)
        if not ok:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Failed to update indexer")
        return {"success": True, "id": indexer_id, "enable": body.enable}
    finally:
        await connector.close()


@router.get("/history", response_model=list[ProwlarrHistoryItem])
async def get_history(limit: int = Query(default=15, ge=1, le=100), db: Session = Depends(get_db)):
    """Return recent Prowlarr history."""
    connector = _get_connector(db)
    try:
        return await connector.get_history(page_size=limit)
    finally:
        await connector.close()


@router.get("/search", response_model=list[ProwlarrSearchResult])
async def search(
    query: str = Query(..., min_length=1),
    type: str = Query(default="search"),
    db: Session = Depends(get_db),
):
    """Search across all active Prowlarr indexers."""
    connector = _get_connector(db)
    try:
        return await connector.search(query, type)
    finally:
        await connector.close()


@router.post("/grab")
async def grab(body: ProwlarrGrabRequest, db: Session = Depends(get_db)):
    """Grab a search result (send to download client)."""
    connector = _get_connector(db)
    try:
        ok = await connector.grab(body.guid, body.indexerId)
        if not ok:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Failed to grab result")
        return {"success": True}
    finally:
        await connector.close()
