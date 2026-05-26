from fastapi import APIRouter, HTTPException
from app.infrastructure.incident_repository import IncidentRepository
import logging

logger = logging.getLogger("voltedge.charging-session")

router = APIRouter(prefix="/incidents", tags=["Incidents"])
repository = IncidentRepository()

@router.get("/")
def get_incidents(severity: str = None, charger_id: str = None):
    try:
        incidents = repository.get_all(severity=severity, charger_id=charger_id)
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
        incident = repository.get_by_id(incident_id)
        if not incident:
            raise HTTPException(status_code=404, detail=f"Incident {incident_id} ikke fundet")
        logger.info(f"Hentet incident {incident_id}")
        return incident
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fejl ved hentning af incident {incident_id}: {e}")
        raise HTTPException(status_code=500, detail="Fejl ved hentning af incident")