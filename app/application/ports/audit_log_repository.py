from typing import Protocol, Dict, Any
from uuid import UUID


class AuditLogRepository(Protocol):
    async def log_event(
        self,
        *,
        verification_id: UUID,
        event_type: str,
        payload: Dict[str, Any],
        actor: Dict[str, Any] | None = None,
    ) -> None: ...
