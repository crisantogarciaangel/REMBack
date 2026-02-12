from __future__ import annotations

from typing import Optional, Protocol, Sequence
from uuid import UUID

from app.domain.entities.verification_request import VerificationRequest
from app.domain.enums.verification_status import VerificationStatus


class VerificationRepository(Protocol):
    def create(self, item: VerificationRequest) -> VerificationRequest: ...
    def list(
        self,
        *,
        search: Optional[str] = None,
        status: Optional[VerificationStatus] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[VerificationRequest]: ...
    def get_by_id(self, verification_id: UUID) -> Optional[VerificationRequest]: ...
    def update(self, item: VerificationRequest) -> VerificationRequest: ...
