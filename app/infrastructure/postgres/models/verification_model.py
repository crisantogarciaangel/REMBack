from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid

from app.infrastructure.postgres.database import Base


class VerificationModel(Base):
    __tablename__ = "verification_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False, index=True)
    phone = Column(String, nullable=False)
    country = Column(String, nullable=False, index=True)
    document_type = Column(String, nullable=False)
    document_number = Column(String, nullable=False)
    document_url = Column(String, nullable=False)
    status = Column(String, nullable=False, index=True)
    risk_score = Column(Integer, nullable=False)
    risk_level = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
