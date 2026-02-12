from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from app.domain.enums.verification_status import VerificationStatus
from app.domain.enums.risk_level import RiskLevel


@dataclass
class VerificationRequest:
    id: UUID
    full_name: str
    email: str
    phone: str
    country: str
    document_type: str
    document_number: str
    document_url: str
    status: VerificationStatus
    risk_score: int
    risk_level: RiskLevel
    created_at: datetime
