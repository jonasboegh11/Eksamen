from fastapi import APIRouter, HTTPException
from app.infrastructure.analytics_repository import AnalyticsRepository
from app.domain.prediction_service import PredictionService, ChargerFeatures
import logging

logger = logging.getLogger("voltedge.charging-session")

router = APIRouter(prefix="/analytics", tags=["Analytics"])
repository = AnalyticsRepository()
prediction_service = PredictionService()

@router.get("/incidents-per-severity")
def incidents_per_severity():
    try:
        results = repository.get_incidents_per_severity()
        logger.info("Analytics: incidents per severity hentet")
        return {"incidents_per_severity": results}
    except Exception as e:
        logger.error(f"Fejl ved analytics: {e}")
        raise HTTPException(status_code=500, detail="Fejl ved analytics")

@router.get("/incidents-per-charger")
def incidents_per_charger():
    try:
        results = repository.get_incidents_per_charger()
        logger.info("Analytics: incidents per lader hentet")
        return {"incidents_per_charger": results}
    except Exception as e:
        logger.error(f"Fejl ved analytics: {e}")
        raise HTTPException(status_code=500, detail="Fejl ved analytics")

@router.get("/most-problematic-charger")
def most_problematic_charger():
    try:
        result = repository.get_most_problematic_charger()
        if not result:
            return {"message": "Ingen incidents registreret endnu"}
        logger.info(f"Analytics: mest problematiske lader er {result['charger_id']}")
        return {"most_problematic_charger": result}
    except Exception as e:
        logger.error(f"Fejl ved analytics: {e}")
        raise HTTPException(status_code=500, detail="Fejl ved analytics")

@router.get("/summary")
def summary():
    try:
        result = repository.get_summary()
        logger.info("Analytics: summary hentet")
        return {"summary": result}
    except Exception as e:
        logger.error(f"Fejl ved analytics: {e}")
        raise HTTPException(status_code=500, detail="Fejl ved analytics")

@router.get("/predict/{charger_id}")
def predict_risk(charger_id: str):
    try:
        result = repository.get_incidents_last_24h(charger_id)

        total = result["total"] or 0
        critical_count = result["critical_count"] or 0
        avg_value = float(result["avg_value"] or 0)
        critical_ratio = critical_count / total if total > 0 else 0.0

        features = ChargerFeatures(
            charger_id=charger_id,
            total_incidents_24h=total,
            critical_count_24h=critical_count,
            high_count_24h=result["high_count"] or 0,
            critical_ratio=critical_ratio,
            avg_value=avg_value
        )

        prediction = prediction_service.predict(features)
        logger.info(f"Prediction for {charger_id}: {prediction.risk_level} ({prediction.risk_score})")

        return {
            "charger_id": prediction.charger_id,
            "risk_score": prediction.risk_score,
            "risk_level": prediction.risk_level,
            "recommendation": prediction.recommendation,
            "based_on_incidents": prediction.based_on_incidents,
            "predicted_at": prediction.predicted_at
        }

    except Exception as e:
        logger.error(f"Fejl ved prediction: {e}")
        raise HTTPException(status_code=500, detail="Fejl ved prediction")