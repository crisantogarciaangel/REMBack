from app.domain.enums.risk_level import RiskLevel


class RiskEngine:

    RISK_EMAIL_DOMAINS = ["tempmail.com", "mailinator.com"]
    RESTRICTED_COUNTRIES = ["NK", "IR"]

    def calculate(self, email: str, country: str, document_number: str):
        score = 0

        domain = email.split("@")[-1]

        if domain in self.RISK_EMAIL_DOMAINS:
            score += 40

        if country in self.RESTRICTED_COUNTRIES:
            score += 30

        if len(document_number) < 6:
            score += 30

        return score, self._get_level(score)

    def _get_level(self, score: int) -> RiskLevel:
        if score < 30:
            return RiskLevel.LOW
        elif score < 70:
            return RiskLevel.MEDIUM
        return RiskLevel.HIGH
