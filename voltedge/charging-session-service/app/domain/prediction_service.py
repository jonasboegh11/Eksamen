from dataclasses import dataclass
from datetime import datetime, timezone

# Value Object — input features til ML model
@dataclass(frozen=True)
class ChargerFeatures:
    charger_id: str
    total_incidents_24h: int
    critical_count_24h: int
    high_count_24h: int
    critical_ratio: float
    avg_value: float

# Value Object — forudsigelsesresultat
@dataclass(frozen=True)
class PredictionResult:
    charger_id: str
    risk_score: float
    risk_level: str
    recommendation: str
    based_on_incidents: int
    predicted_at: datetime

# Domain Service — forudsiger risiko baseret på historisk data
class PredictionService:

    def predict(self, features: ChargerFeatures) -> PredictionResult:
        score = 0.0

        # Faktor 1: Antal incidents de sidste 24 timer
        if features.total_incidents_24h >= 5:
            score += 0.4
        elif features.total_incidents_24h >= 3:
            score += 0.25
        elif features.total_incidents_24h >= 1:
            score += 0.1

        # Faktor 2: Andel af kritiske incidents
        if features.critical_ratio >= 0.5:
            score += 0.4
        elif features.critical_ratio >= 0.25:
            score += 0.2
        elif features.critical_ratio > 0:
            score += 0.1

        # Faktor 3: Gennemsnitlig måleværdi
        if features.avg_value > 40:
            score += 0.2
        elif features.avg_value > 22:
            score += 0.1

        score = min(score, 1.0)

        if score >= 0.7:
            risk_level = "critical"
            recommendation = f"Lader {features.charger_id} kræver øjeblikkelig inspektion"
        elif score >= 0.4:
            risk_level = "high"
            recommendation = f"Lader {features.charger_id} bør inspiceres inden for 4 timer"
        elif score >= 0.2:
            risk_level = "medium"
            recommendation = f"Lader {features.charger_id} bør overvåges tæt"
        else:
            risk_level = "low"
            recommendation = f"Lader {features.charger_id} ser ud til at fungere normalt"

        return PredictionResult(
            charger_id=features.charger_id,
            risk_score=round(score, 2),
            risk_level=risk_level,
            recommendation=recommendation,
            based_on_incidents=features.total_incidents_24h,
            predicted_at=datetime.now(timezone.utc)
        )