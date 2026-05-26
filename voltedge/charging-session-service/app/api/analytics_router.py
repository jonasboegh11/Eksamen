from fastapi import APIRouter, HTTPException
from app.infrastructure.database import get_connection
from app.domain.prediction_service import PredictionService, ChargerFeatures
import logging

logger = logging.getLogger("voltedge.charging-session")

router = APIRouter(prefix="/analytics", tags=["Analytics"])
prediction_service = PredictionService()

@router.get("/incidents-per-severity")
def incidents_per_severity():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT severity, COUNT(*) as count
            FROM incidents
            GROUP BY severity
            ORDER BY FIELD(severity, 'critical', 'high', 'medium', 'low')
        """)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        logger.info("Analytics: incidents per severity hentet")
        return {"incidents_per_severity": results}
    except Exception as e:
        logger.error(f"Fejl ved analytics: {e}")
        raise HTTPException(status_code=500, detail="Fejl ved analytics")

@router.get("/incidents-per-charger")
def incidents_per_charger():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT charger_id, COUNT(*) as count,
                   MAX(timestamp) as latest_incident
            FROM incidents
            GROUP BY charger_id
            ORDER BY count DESC
        """)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        logger.info("Analytics: incidents per lader hentet")
        return {"incidents_per_charger": results}
    except Exception as e:
        logger.error(f"Fejl ved analytics: {e}")
        raise HTTPException(status_code=500, detail="Fejl ved analytics")

@router.get("/most-problematic-charger")
def most_problematic_charger():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT charger_id, COUNT(*) as incident_count,
                   MAX(timestamp) as latest_incident,
                   SUM(CASE WHEN severity = 'critical' THEN 1 ELSE 0 END) as critical_count,
                   SUM(CASE WHEN severity = 'high' THEN 1 ELSE 0 END) as high_count
            FROM incidents
            GROUP BY charger_id
            ORDER BY incident_count DESC
            LIMIT 1
        """)
        result = cursor.fetchone()
        cursor.close()
        conn.close()
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
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                COUNT(*) as total_incidents,
                SUM(CASE WHEN severity = 'critical' THEN 1 ELSE 0 END) as critical,
                SUM(CASE WHEN severity = 'high' THEN 1 ELSE 0 END) as high,
                SUM(CASE WHEN severity = 'medium' THEN 1 ELSE 0 END) as medium,
                SUM(CASE WHEN severity = 'low' THEN 1 ELSE 0 END) as low,
                COUNT(DISTINCT charger_id) as affected_chargers,
                MAX(timestamp) as latest_incident
            FROM incidents
        """)
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        logger.info("Analytics: summary hentet")
        return {"summary": result}
    except Exception as e:
        logger.error(f"Fejl ved analytics: {e}")
        raise HTTPException(status_code=500, detail="Fejl ved analytics")

@router.get("/predict/{charger_id}")
def predict_risk(charger_id: str):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Hent incidents de sidste 24 timer
        cursor.execute("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN severity = 'critical' THEN 1 ELSE 0 END) as critical_count,
                SUM(CASE WHEN severity = 'high' THEN 1 ELSE 0 END) as high_count,
                AVG(value) as avg_value
            FROM incidents
            WHERE charger_id = %s
            AND timestamp >= NOW() - INTERVAL 24 HOUR
        """, (charger_id,))

        result = cursor.fetchone()
        cursor.close()
        conn.close()

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