from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.domain.enums.verification_status import VerificationStatus


class VerificationCreateRequest(BaseModel):
    full_name: str = Field(min_length=3, max_length=200)
    email: EmailStr
    phone: str = Field(min_length=8, max_length=15, pattern=r"^\d+$")
    country: str = Field(min_length=2, max_length=3)
    document_type: str = Field(min_length=2, max_length=50)
    document_number: str = Field(min_length=3, max_length=50)
    document_url: str = Field(min_length=5, max_length=500)


class VerificationStatusUpdateRequest(BaseModel):
    status: VerificationStatus


class VerificationResponse(BaseModel):
    id: UUID
    full_name: str
    email: EmailStr
    phone: str
    country: str
    document_type: str
    document_number: str
    document_url: str
    status: VerificationStatus
    risk_score: int
    risk_level: str
    created_at: datetime


class VerificationListResponse(BaseModel):
    items: List[VerificationResponse]
    limit: int
    offset: int
    total: Optional[int] = None
