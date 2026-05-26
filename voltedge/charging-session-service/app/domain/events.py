from pydantic import BaseModel, Field
from datetime import datetime, timezone
from enum import Enum
import uuid

class DomainEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Telemetriindsamling events
class TelemetryReceived(DomainEvent):
    charger_id: str
    power_kw: float
    voltage: float
    current: float
    status: str

class TelemetryValidated(DomainEvent):
    charger_id: str

class TelemetryStored(DomainEvent):
    charger_id: str

class TelemetryRejected(DomainEvent):
    charger_id: str
    reason: str

# Anomalidetektion events
class AnomalyDetected(DomainEvent):
    charger_id: str
    anomaly_type: str
    value: float
    threshold: float

class AnomalyClassified(DomainEvent):
    charger_id: str
    anomaly_type: str
    severity: str

class ThresholdExceeded(DomainEvent):
    charger_id: str
    rule_name: str
    value: float
    threshold: float

class AlarmTriggered(DomainEvent):
    charger_id: str
    severity: str
    rule_name: str
    message: str
    value: float
    threshold: float

# Incidentoprettelse events
class IncidentCreated(DomainEvent):
    incident_id: str
    charger_id: str
    severity: str
    rule_name: str

class IncidentClassified(DomainEvent):
    incident_id: str
    severity: str

class TechnicianAssignedToIncident(DomainEvent):
    incident_id: str
    technician_id: str

# Incidenteskalering events
class IncidentResolved(DomainEvent):
    incident_id: str
    resolved_by: str

class IncidentEscalated(DomainEvent):
    incident_id: str
    reason: str