from fastapi import APIRouter, HTTPException
from app.domain.telemetry import Telemetry
from app.domain.charger import ChargerDevice
from app.domain.rule_engine import evaluate
from app.infrastructure.incident_repository import IncidentRepository
import logging

logger = logging.getLogger("voltedge.charging-session")

router = APIRouter(prefix="/telemetry", tags=["Telemetry"])
repository = IncidentRepository()

@router.post("/")
def receive_telemetry(telemetry: Telemetry):
    stream = telemetry.to_stream()
    logger.info(f"Telemetri modtaget fra lader {stream.charger_id} | {stream.measurement.power_kw} kW | {stream.status}")

    charger = ChargerDevice(
        charger_id=stream.charger_id,
        status=stream.status.value
    )

    charger.receive_telemetry(telemetry)
    incidents = evaluate(telemetry)

    for incident in incidents:
        charger.add_incident(incident)

    if incidents:
        try:
            for incident in incidents:
                logger.warning(f"INCIDENT [{incident.severity.upper()}] | {incident.rule_name} | {incident.message}")
                repository.save(incident)
            logger.info(f"{len(incidents)} incident(s) gemt i databasen")
        except Exception as e:
            logger.error(f"Fejl ved gemning af incidents: {e}")
            raise HTTPException(status_code=500, detail="Fejl ved gemning af incidents")
    else:
        logger.info(f"Ingen incidents for lader {telemetry.charger_id}")

    return {
        "charger_id": charger.charger_id,
        "status": charger.status,
        "has_critical_incidents": charger.has_critical_incidents(),
        "incidents_count": len(incidents),
        "incidents": incidents
    }