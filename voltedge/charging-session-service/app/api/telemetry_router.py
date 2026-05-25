from fastapi import APIRouter
from app.domain.telemetry import Telemetry
from app.domain.rule_engine import evaluate
import logging

logger = logging.getLogger("voltedge.charging-session")

router = APIRouter(prefix="/telemetry", tags=["Telemetry"])

@router.post("/")
def receive_telemetry(telemetry: Telemetry):
    logger.info(f"Telemetri modtaget fra lader {telemetry.charger_id} | {telemetry.power_kw} kW | {telemetry.status}")
    
    incidents = evaluate(telemetry)
    
    if incidents:
        for incident in incidents:
            logger.warning(f"INCIDENT [{incident.severity.upper()}] | {incident.rule_name} | {incident.message}")
    else:
        logger.info(f"Ingen incidents for lader {telemetry.charger_id}")

    return {
        "charger_id": telemetry.charger_id,
        "incidents_count": len(incidents),
        "incidents": incidents
    }