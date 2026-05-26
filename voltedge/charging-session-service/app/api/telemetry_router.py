from fastapi import APIRouter, HTTPException
from app.domain.telemetry import Telemetry
from app.domain.charger import ChargerDevice
from app.domain.rule_engine import evaluate
from app.infrastructure.database import get_connection
import logging

logger = logging.getLogger("voltedge.charging-session")

router = APIRouter(prefix="/telemetry", tags=["Telemetry"])

@router.post("/")
def receive_telemetry(telemetry: Telemetry):
    logger.info(f"Telemetri modtaget fra lader {telemetry.charger_id} | {telemetry.power_kw} kW | {telemetry.status}")

    charger = ChargerDevice(
        charger_id=telemetry.charger_id,
        status=telemetry.status.value
    )

    charger.receive_telemetry(telemetry)
    incidents = evaluate(telemetry)

    for incident in incidents:
        charger.add_incident(incident)

    if incidents:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            for incident in incidents:
                logger.warning(f"INCIDENT [{incident.severity.upper()}] | {incident.rule_name} | {incident.message}")
                cursor.execute("""
                    INSERT INTO incidents (incident_id, charger_id, severity, rule_name, message, value, threshold, timestamp, status, sla_deadline)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    incident.incident_id,
                    incident.charger_id,
                    incident.severity,
                    incident.rule_name,
                    incident.message,
                    incident.value,
                    incident.threshold,
                    incident.timestamp,
                    incident.status,
                    incident.sla_deadline.deadline
                ))
            conn.commit()
            cursor.close()
            conn.close()
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