from datetime import datetime, timezone
from typing import Optional, Sequence
from uuid import UUID

from app.application.services.verification_service import VerificationService
from app.domain.entities.verification_request import VerificationRequest
from app.domain.enums.verification_status import VerificationStatus


class FakeVerificationRepository:
    def __init__(self):
        self.items = {}

    def create(self, item: VerificationRequest) -> VerificationRequest:
        self.items[item.id] = item
        return item

    def list(
        self,
        *,
        search: Optional[str] = None,
        status: Optional[VerificationStatus] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[VerificationRequest]:
        data = list(self.items.values())
        if status is not None:
            data = [x for x in data if x.status == status]
        return data[offset : offset + limit]

    def get_by_id(self, verification_id: UUID) -> Optional[VerificationRequest]:
        return self.items.get(verification_id)

    def update(self, item: VerificationRequest) -> VerificationRequest:
        self.items[item.id] = item
        return item


def test_service_create_sets_pending_and_persists_entity():
    repo = FakeVerificationRepository()
    fixed_now = datetime(2026, 2, 13, 0, 0, 0, tzinfo=timezone.utc)
    service = VerificationService(repo=repo, now_provider=lambda: fixed_now)

    created = service.create(
        full_name="Juan Perez",
        email="juan.perez@test.com",
        phone="5512345678",
        country="mx",
        document_type="INE",
        document_number="ABC123456",
        document_url="https://example.com/doc.jpg",
    )

    assert created.status == VerificationStatus.PENDING
    assert created.created_at == fixed_now
    assert created.id in repo.items
