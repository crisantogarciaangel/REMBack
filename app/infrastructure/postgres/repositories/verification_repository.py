from __future__ import annotations

from typing import Optional, Sequence
from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.application.ports.verification_repository import VerificationRepository
from app.domain.entities.verification_request import VerificationRequest
from app.domain.enums.risk_level import RiskLevel
from app.domain.enums.verification_status import VerificationStatus
from app.infrastructure.postgres.models.verification_model import VerificationModel


class PostgresVerificationRepository(VerificationRepository):
    def __init__(self, session: Session):
        self._session = session

    def create(self, item: VerificationRequest) -> VerificationRequest:
        model = VerificationModel(
            id=item.id,
            full_name=item.full_name,
            email=item.email,
            phone=item.phone,
            country=item.country,
            document_type=item.document_type,
            document_number=item.document_number,
            document_url=item.document_url,
            status=item.status.value,
            risk_score=item.risk_score,
            risk_level=item.risk_level.value,
            created_at=item.created_at,
        )
        self._session.add(model)
        self._session.commit()
        return item

    def list(
        self,
        *,
        search: Optional[str] = None,
        status: Optional[VerificationStatus] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[VerificationRequest]:
        q = self._session.query(VerificationModel)

        if search:
            q = q.filter(
                or_(
                    VerificationModel.full_name.ilike(f"%{search}%"),
                    VerificationModel.email.ilike(f"%{search}%"),
                )
            )

        if status:
            q = q.filter(VerificationModel.status == status.value)

        rows = (
            q.order_by(VerificationModel.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

        return [self._to_entity(r) for r in rows]

    def get_by_id(self, verification_id: UUID) -> Optional[VerificationRequest]:
        row = (
            self._session.query(VerificationModel)
            .filter(VerificationModel.id == verification_id)
            .first()
        )
        return self._to_entity(row) if row else None

    def update(self, item: VerificationRequest) -> VerificationRequest:
        row = (
            self._session.query(VerificationModel)
            .filter(VerificationModel.id == item.id)
            .first()
        )
        if row is None:
            raise LookupError("verification not found")

        row.status = item.status.value
        self._session.commit()
        return item

    def _to_entity(self, row: VerificationModel) -> VerificationRequest:
        return VerificationRequest(
            id=row.id,
            full_name=row.full_name,
            email=row.email,
            phone=row.phone,
            country=row.country,
            document_type=row.document_type,
            document_number=row.document_number,
            document_url=row.document_url,
            status=VerificationStatus(row.status),
            risk_score=row.risk_score,
            risk_level=RiskLevel(row.risk_level),
            created_at=row.created_at,
        )
