from app.infrastructure.postgres.database import engine, Base
from app.infrastructure.postgres.models.verification_model import VerificationModel


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
