from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from typing import Optional, Sequence
from uuid import UUID, uuid4

from app.domain.entities.verification_request import VerificationRequest
from app.domain.enums.verification_status import VerificationStatus
from app.domain.rules.risk_engine import RiskEngine
from app.application.ports.verification_repository import VerificationRepository


class VerificationService:
    def __init__(
        self,
        repo: VerificationRepository,
        risk_engine: Optional[RiskEngine] = None,
        now_provider=None,
    ) -> None:
        self._repo = repo
        self._risk_engine = risk_engine or RiskEngine()
        self._now = now_provider or (lambda: datetime.now(timezone.utc))

    def create(
        self,
        *,
        full_name: str,
        email: str,
        phone: str,
        country: str,
        document_type: str,
        document_number: str,
        document_url: str,
    ) -> VerificationRequest:
        self._validate_create_inputs(
            full_name=full_name,
            email=email,
            phone=phone,
            country=country,
            document_type=document_type,
            document_number=document_number,
            document_url=document_url,
        )

        risk_score, risk_level = self._risk_engine.calculate(
            email=email,
            country=country,
            document_number=document_number,
        )

        entity = VerificationRequest(
            id=uuid4(),
            full_name=full_name.strip(),
            email=email.strip().lower(),
            phone=phone.strip(),
            country=country.strip().upper(),
            document_type=document_type.strip(),
            document_number=document_number.strip(),
            document_url=document_url.strip(),
            status=VerificationStatus.PENDING,
            risk_score=risk_score,
            risk_level=risk_level,
            created_at=self._now(),
        )

        return self._repo.create(entity)

    def list(
        self,
        *,
        search: Optional[str] = None,
        status: Optional[VerificationStatus] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[VerificationRequest]:
        if limit < 1 or limit > 200:
            raise ValueError("limit must be between 1 and 200")
        if offset < 0:
            raise ValueError("offset must be >= 0")

        s = search.strip() if search else None
        return self._repo.list(search=s, status=status, limit=limit, offset=offset)

    def get(self, verification_id: UUID) -> VerificationRequest:
        item = self._repo.get_by_id(verification_id)
        if item is None:
            raise LookupError("verification not found")
        return item

    def update_status(
        self,
        *,
        verification_id: UUID,
        new_status: VerificationStatus,
    ) -> VerificationRequest:
        current = self._repo.get_by_id(verification_id)
        if current is None:
            raise LookupError("verification not found")

        self._validate_status_transition(current.status, new_status)

        updated = replace(current, status=new_status)
        return self._repo.update(updated)

    def _validate_create_inputs(
        self,
        *,
        full_name: str,
        email: str,
        phone: str,
        country: str,
        document_type: str,
        document_number: str,
        document_url: str,
    ) -> None:
        if not full_name or len(full_name.strip()) < 3:
            raise ValueError("full_name is required")

        e = (email or "").strip()
        if "@" not in e or e.startswith("@") or e.endswith("@"):
            raise ValueError("email is invalid")

        p = (phone or "").strip()
        if len(p) < 8 or len(p) > 20:
            raise ValueError("phone is invalid")

        c = (country or "").strip()
        if len(c) < 2:
            raise ValueError("country is required")

        dt = (document_type or "").strip()
        if len(dt) < 2:
            raise ValueError("document_type is required")

        dn = (document_number or "").strip()
        if len(dn) < 3:
            raise ValueError("document_number is required")

        du = (document_url or "").strip()
        if len(du) < 5:
            raise ValueError("document_url is required")

    def _validate_status_transition(
        self,
        current: VerificationStatus,
        new: VerificationStatus,
    ) -> None:
        final_states = {VerificationStatus.APPROVED, VerificationStatus.REJECTED}
        if current in final_states and new != current:
            raise ValueError("cannot change status from a final state")
