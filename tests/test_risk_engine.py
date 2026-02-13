from app.domain.rules.risk_engine import RiskEngine
from app.domain.enums.risk_level import RiskLevel


def test_risk_engine_high_risk_when_email_country_and_doc_trigger_rules():
    engine = RiskEngine()

    score, level = engine.calculate(
        email="user@mailinator.com",
        country="IR",
        document_number="123",
    )

    assert score >= 70
    assert level == RiskLevel.HIGH
