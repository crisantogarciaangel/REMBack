import asyncio
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.orm import Session

from app.infrastructure.postgres.database import SessionLocal
from app.infrastructure.postgres.models.verification_model import VerificationModel

try:
    from app.infrastructure.mongo.database import db
except Exception:
    db = None


SAMPLE = [
    {
        "full_name": "Emanuel Garcia",
        "email": "emanuel.garcia@test.com",
        "phone": "5512345678",
        "country": "MX",
        "document_type": "INE",
        "document_number": "ABC123456",
        "document_url": "https://example.com/doc-emanuel.jpg",
        "status": "pending",
        "risk_score": 10,
        "risk_level": "low",
    },
    {
        "full_name": "Miriam Venegas",
        "email": "Miriam.Venegas@mailinator.com",
        "phone": "5587654321",
        "country": "MX",
        "document_type": "PASSPORT",
        "document_number": "P1234567",
        "document_url": "https://example.com/doc-Venegas.jpg",
        "status": "requires_information",
        "risk_score": 55,
        "risk_level": "medium",
    },
    {
        "full_name": "Pedro Reyes",
        "email": "Pedro.Reyes@test.com",
        "phone": "5511122233",
        "country": "IR",
        "document_type": "LICENSE",
        "document_number": "12",
        "document_url": "https://example.com/doc-Reyes.jpg",
        "status": "rejected",
        "risk_score": 85,
        "risk_level": "high",
    },
]


def seed_postgres() -> int:
    session: Session = SessionLocal()
    inserted = 0
    now = datetime.now(timezone.utc)

    try:
        for item in SAMPLE:
            exists = (
                session.query(VerificationModel)
                .filter(VerificationModel.email == item["email"])
                .first()
            )
            if exists:
                continue

            model = VerificationModel(
                id=uuid4(),
                full_name=item["full_name"],
                email=item["email"],
                phone=item["phone"],
                country=item["country"],
                document_type=item["document_type"],
                document_number=item["document_number"],
                document_url=item["document_url"],
                status=item["status"],
                risk_score=item["risk_score"],
                risk_level=item["risk_level"],
                created_at=now,
            )
            session.add(model)
            inserted += 1

        session.commit()
        return inserted
    finally:
        session.close()


async def seed_mongo() -> int:
    if db is None:
        print("Mongo: skipped (not configured)")
        return 0

    try:
        collection = db["verification_audit_logs"]
        inserted = 0
        now = datetime.now(timezone.utc)

        for item in SAMPLE:
            exists = await collection.find_one(
                {"event_type": "seed_created", "payload.email": item["email"]}
            )
            if exists:
                continue

            await collection.insert_one(
                {
                    "event_id": str(uuid4()),
                    "verification_id": None,
                    "event_type": "seed_created",
                    "payload": {
                        "email": item["email"],
                        "country": item["country"],
                        "risk_level": item["risk_level"],
                    },
                    "actor": {"type": "system"},
                    "created_at": now,
                }
            )
            inserted += 1

        return inserted
    except Exception as e:
        print(f"Mongo: failed to seed ({e})")
        return 0


def main():
    pg_inserted = seed_postgres()
    mongo_inserted = asyncio.run(seed_mongo())

    print(f"Postgres: inserted {pg_inserted} sample records")
    print(f"Mongo: inserted {mongo_inserted} sample audit events")


if __name__ == "__main__":
    main()
