from fastapi import APIRouter, HTTPException
from app.domain.telemetry import Telemetry
from app.domain.charger import ChargerDevice
from app.domain.anomaly import Anomaly
from app.domain.incident import Incident
from app.domain.events import AlarmTriggered, TelemetryStored, TelemetryRejected
from app.infrastructure.incident_repository import IncidentRepository
import logging

logger = logging.getLogger("voltedge.charging-session")

router = APIRouter(prefix="/telemetry", tags=["Telemetry"])
repository = IncidentRepository()

@router.post("/")
def receive_telemetry(telemetry: Telemetry):
    stream = telemetry.to_stream()
    logger.info(f"Telemetri modtaget fra lader {stream.charger_id} | {stream.measurement.power_kw} kW | {stream.status}")

    try:
        charger = ChargerDevice(
            charger_id=stream.charger_id,
            status=stream.status.value
        )
        charger.receive_telemetry(telemetry)

        stored_event = TelemetryStored(charger_id=telemetry.charger_id)
        logger.info(f"EVENT: TelemetryStored | {stored_event.charger_id}")

    except Exception as e:
        rejected_event = TelemetryRejected(charger_id=telemetry.charger_id, reason=str(e))
        logger.warning(f"EVENT: TelemetryRejected | {rejected_event.charger_id} | {rejected_event.reason}")
        raise HTTPException(status_code=422, detail=str(e))

    anomaly = Anomaly(charger_id=telemetry.charger_id)
    anomaly_events = anomaly.analyze(telemetry)

    for event in anomaly_events:
        logger.info(f"EVENT: {event.__class__.__name__} | {event.charger_id}")

    incidents = []
    try:
        for event in anomaly_events:
            if isinstance(event, AlarmTriggered):
                incident = Incident(
                    charger_id=event.charger_id,
                    severity=event.severity,
                    rule_name=event.rule_name,
                    message=event.message,
                    value=event.value,
                    threshold=event.threshold
                )
                charger.add_incident(incident)
                repository.save(incident)
                incidents.append(incident)
                logger.warning(f"EVENT: IncidentCreated | {incident.incident_id} | [{incident.severity.upper()}] {incident.rule_name}")

        if incidents:
            logger.info(f"{len(incidents)} incident(s) gemt i databasen")
        else:
            logger.info(f"Ingen incidents for lader {telemetry.charger_id}")

    except Exception as e:
        logger.error(f"Fejl ved gemning af incidents: {e}")
        raise HTTPException(status_code=500, detail="Fejl ved gemning af incidents")

    return {
        "charger_id": charger.charger_id,
        "status": charger.status,
        "has_critical_incidents": charger.has_critical_incidents(),
        "incidents_count": len(incidents),
        "incidents": [
            incident.model_dump(exclude={"events"})
            for incident in incidents
        ]
    }