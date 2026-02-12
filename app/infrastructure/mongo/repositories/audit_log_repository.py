from datetime import datetime, timezone
from typing import Dict, Any
from uuid import UUID, uuid4

from app.application.ports.audit_log_repository import AuditLogRepository
from app.infrastructure.mongo.database import db


class MongoAuditLogRepository(AuditLogRepository):
    def __init__(self):
        self._collection = db["verification_audit_logs"]

    async def log_event(
        self,
        *,
        verification_id: UUID,
        event_type: str,
        payload: Dict[str, Any],
        actor: Dict[str, Any] | None = None,
    ) -> None:
        await self._collection.insert_one(
            {
                "event_id": str(uuid4()),
                "verification_id": str(verification_id),
                "event_type": event_type,
                "payload": payload,
                "actor": actor,
                "created_at": datetime.now(timezone.utc),
            }
        )
