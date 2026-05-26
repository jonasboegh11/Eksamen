from fastapi import APIRouter, HTTPException
from app.infrastructure.database import get_connection
import logging

logger = logging.getLogger("voltedge.charging-session")

router = APIRouter(prefix="/analytics", tags=["Analytics"])

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