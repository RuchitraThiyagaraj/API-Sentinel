"""
routers/apis.py
----------------
GET  /apis                       -> list current user's APIs (with latest status + uptime)
POST /apis                       -> add a new API manually
GET  /apis/{id}                  -> details of one API (with total/success/fail counts)
GET  /apis/{id}/history           -> monitoring history (for the graph + table)
POST /apis/import-documentation  -> send pasted docs to the LLM, return extracted fields

Every endpoint here verifies api.user_id == current_user.id before
returning or modifying anything, so a user can only ever see their own APIs.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
import models
import schemas
from auth_utils import get_current_user
from services.llm import extract_api_info

router = APIRouter(prefix="/apis", tags=["apis"])


def _get_owned_api_or_404(db: Session, api_id: int, user: models.User) -> models.Api:
    api = db.query(models.Api).filter(models.Api.id == api_id).first()
    if not api or api.user_id != user.id:
        raise HTTPException(status_code=404, detail="API not found")
    return api


def _build_api_response(db: Session, api: models.Api) -> schemas.ApiResponse:
    """Attaches latest check status + uptime % to a bare Api row."""
    latest = (
        db.query(models.MonitoringResult)
        .filter(models.MonitoringResult.api_id == api.id)
        .order_by(models.MonitoringResult.checked_at.desc())
        .first()
    )

    total = (
        db.query(func.count(models.MonitoringResult.id))
        .filter(models.MonitoringResult.api_id == api.id)
        .scalar()
    )
    successful = (
        db.query(func.count(models.MonitoringResult.id))
        .filter(
            models.MonitoringResult.api_id == api.id,
            models.MonitoringResult.status != "offline",
        )
        .scalar()
    )
    uptime = round((successful / total) * 100, 2) if total else None

    return schemas.ApiResponse(
        id=api.id,
        name=api.name,
        url=api.url,
        method=api.method,
        created_at=api.created_at,
        status=latest.status if latest else None,
        http_status_code=latest.http_status_code if latest else None,
        response_time=latest.response_time if latest else None,
        last_checked=latest.checked_at if latest else None,
        uptime=uptime,
    )


@router.get("", response_model=List[schemas.ApiResponse])
def list_apis(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    apis = db.query(models.Api).filter(models.Api.user_id == current_user.id).all()
    return [_build_api_response(db, api) for api in apis]


@router.post("", response_model=schemas.ApiResponse, status_code=201)
def create_api(
    payload: schemas.ApiCreateRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    api = models.Api(
        user_id=current_user.id,
        name=payload.name,
        url=payload.url,
        method=payload.method,
        auth_token=payload.auth_token,
    )
    db.add(api)
    db.commit()
    db.refresh(api)
    return _build_api_response(db, api)


@router.get("/{api_id}", response_model=schemas.ApiDetailsResponse)
def get_api_details(
    api_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    api = _get_owned_api_or_404(db, api_id, current_user)
    base = _build_api_response(db, api)

    total = (
        db.query(func.count(models.MonitoringResult.id))
        .filter(models.MonitoringResult.api_id == api.id)
        .scalar()
    )
    successful = (
        db.query(func.count(models.MonitoringResult.id))
        .filter(
            models.MonitoringResult.api_id == api.id,
            models.MonitoringResult.status != "offline",
        )
        .scalar()
    )

    return schemas.ApiDetailsResponse(
        **base.model_dump(),
        total_checks=total,
        successful_checks=successful,
        failed_checks=total - successful,
    )


@router.get("/{api_id}/history", response_model=List[schemas.MonitoringResultResponse])
def get_api_history(
    api_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    api = _get_owned_api_or_404(db, api_id, current_user)

    results = (
        db.query(models.MonitoringResult)
        .filter(models.MonitoringResult.api_id == api.id)
        .order_by(models.MonitoringResult.checked_at.asc())
        .limit(200)
        .all()
    )
    return results


@router.post("/import-documentation", response_model=schemas.ImportDocumentationResponse)
def import_documentation(
    payload: schemas.ImportDocumentationRequest,
    current_user: models.User = Depends(get_current_user),
):
    """
    Sends pasted documentation text to the LLM and returns the extracted
    fields. Does NOT save anything -- the user must confirm via
    POST /apis afterwards. If this fails, the frontend falls back to
    manual entry.
    """
    try:
        extracted = extract_api_info(payload.documentation_text)
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=f"Could not extract API info from documentation: {e}",
        )

    return schemas.ImportDocumentationResponse(**extracted)
