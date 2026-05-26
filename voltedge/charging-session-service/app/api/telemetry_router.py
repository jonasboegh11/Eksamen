from fastapi import APIRouter, HTTPException
from app.domain.telemetry import Telemetry
from app.domain.charger import ChargerDevice
from app.domain.anomaly import Anomaly
from app.domain.incident import Incident
from app.domain.events import AlarmTriggered
from app.infrastructure.incident_repository import IncidentRepository
from app.infrastructure.charger_repository import ChargerRepository
import logging

logger = logging.getLogger("voltedge.charging-session")

router = APIRouter(prefix="/telemetry", tags=["Telemetry"])
repository = IncidentRepository()
charger_repository = ChargerRepository()

@router.post("/")
def receive_telemetry(telemetry: Telemetry):

    # Opret TelemetryStream aggregat og kør aggregat-metoder
    stream = telemetry.to_stream()
    try:
        stream.receive(telemetry)
        logger.info(f"EVENT: TelemetryReceived | {stream.charger_id} | {stream.measurement.power_kw} kW | {stream.status}")
    except Exception as e:
        stream.reject(reason=str(e))
        for event in stream.pull_events():
            logger.warning(f"EVENT: {event.__class__.__name__} | {event.charger_id} | {getattr(event, 'reason', '')}")
        raise HTTPException(status_code=422, detail=str(e))

    # Opret ChargerDevice aggregat og load persisteret state fra db
    try:
        charger = ChargerDevice(
            charger_id=stream.charger_id,
            status=stream.status.value
        )
        has_critical = charger_repository.has_critical_incidents(stream.charger_id)
        charger.set_critical_from_db(has_critical)
        charger.receive_telemetry(telemetry)
        stream.store()
    except Exception as e:
        stream.reject(reason=str(e))
        for event in stream.pull_events():
            logger.warning(f"EVENT: {event.__class__.__name__} | {event.charger_id} | {getattr(event, 'reason', '')}")
        raise HTTPException(status_code=422, detail=str(e))

    # Publish alle TelemetryStream events
    for event in stream.pull_events():
        logger.info(f"EVENT: {event.__class__.__name__} | {event.charger_id}")

    # Anomalidetektion
    anomaly = Anomaly(charger_id=telemetry.charger_id)
    anomaly_events = anomaly.analyze(telemetry)

    for event in anomaly_events:
        logger.info(f"EVENT: {event.__class__.__name__} | {event.charger_id}")

    # Incidentoprettelse
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