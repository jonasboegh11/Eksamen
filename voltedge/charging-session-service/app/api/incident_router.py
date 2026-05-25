from fastapi import APIRouter, HTTPException
from app.infrastructure.database import get_connection
import logging

logger = logging.getLogger("voltedge.charging-session")

router = APIRouter(prefix="/incidents", tags=["Incidents"])

@router.get("/")
def get_incidents(severity: str = None, charger_id: str = None):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM incidents WHERE 1=1"
        params = []

        if severity:
            query += " AND severity = %s"
            params.append(severity)

        if charger_id:
            query += " AND charger_id = %s"
            params.append(charger_id)

        query += " ORDER BY timestamp DESC"

        cursor.execute(query, params)
        incidents = cursor.fetchall()
        cursor.close()
        conn.close()

        logger.info(f"Hentet {len(incidents)} incidents — filters: severity={severity}, charger_id={charger_id}")

        return {
            "count": len(incidents),
            "incidents": incidents
        }

    except Exception as e:
        logger.error(f"Fejl ved hentning af incidents: {e}")
        raise HTTPException(status_code=500, detail="Fejl ved hentning af incidents")

@router.get("/{incident_id}")
def get_incident(incident_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM incidents WHERE id = %s", (incident_id,))
        incident = cursor.fetchone()
        cursor.close()
        conn.close()

        if not incident:
            raise HTTPException(status_code=404, detail=f"Incident {incident_id} ikke fundet")

        logger.info(f"Hentet incident {incident_id}")
        return incident

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fejl ved hentning af incident {incident_id}: {e}")
        raise HTTPException(status_code=500, detail="Fejl ved hentning af incident")