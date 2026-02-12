from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.application.services.verification_service import VerificationService
from app.domain.enums.verification_status import VerificationStatus
from app.infrastructure.postgres.repositories.verification_repository import PostgresVerificationRepository
from app.infrastructure.mongo.repositories.audit_log_repository import MongoAuditLogRepository
from app.schemas.verification import (
    VerificationCreateRequest,
    VerificationResponse,
    VerificationStatusUpdateRequest,
    VerificationListResponse,
)

router = APIRouter(prefix="/verifications", tags=["verifications"])


def _service(db: Session) -> VerificationService:
    repo = PostgresVerificationRepository(db)
    return VerificationService(repo=repo)


@router.post("", response_model=VerificationResponse, status_code=status.HTTP_201_CREATED)
async def create_verification(payload: VerificationCreateRequest, db: Session = Depends(get_db)):
    service = _service(db)
    try:
        created = service.create(
            full_name=payload.full_name,
            email=str(payload.email),
            phone=payload.phone,
            country=payload.country,
            document_type=payload.document_type,
            document_number=payload.document_number,
            document_url=payload.document_url,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    audit = MongoAuditLogRepository()
    try:
        await audit.log_event(
            verification_id=created.id,
            event_type="verification_created",
            payload={"status": created.status.value, "risk_level": str(created.risk_level), "risk_score": created.risk_score},
            actor={"type": "system"},
        )
    except Exception as e:
        print("Mongo error:", e)

    return created


@router.get("", response_model=VerificationListResponse)
async def list_verifications(
    search: Optional[str] = Query(default=None, min_length=1, max_length=200),
    status_filter: Optional[VerificationStatus] = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    service = _service(db)
    try:
        items = service.list(search=search, status=status_filter, limit=limit, offset=offset)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"items": list(items), "limit": limit, "offset": offset, "total": None}


@router.get("/{verification_id}", response_model=VerificationResponse)
async def get_verification(verification_id: UUID, db: Session = Depends(get_db)):
    service = _service(db)
    try:
        item = service.get(verification_id)
    except LookupError:
        raise HTTPException(status_code=404, detail="verification not found")
    return item


@router.patch("/{verification_id}/status", response_model=VerificationResponse)
async def update_status(
    verification_id: UUID,
    payload: VerificationStatusUpdateRequest,
    db: Session = Depends(get_db),
):
    service = _service(db)
    try:
        updated = service.update_status(verification_id=verification_id, new_status=payload.status)
    except LookupError:
        raise HTTPException(status_code=404, detail="verification not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    audit = MongoAuditLogRepository()
    try:
        await audit.log_event(
            verification_id=updated.id,
            event_type="status_updated",
            payload={"new_status": updated.status.value},
            actor={"type": "operator"},
        )
    except Exception:
        pass

    return updated
