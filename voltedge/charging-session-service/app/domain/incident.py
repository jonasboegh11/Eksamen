from pydantic import BaseModel, Field
from datetime import datetime, timezone, timedelta
from enum import Enum
import uuid
from app.domain.events import IncidentCreated, IncidentClassified, TechnicianAssignedToIncident, IncidentResolved, IncidentEscalated

class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class IncidentStatus(str, Enum):
    OPEN = "open"
    ASSIGNED = "assigned"
    RESOLVED = "resolved"
    ESCALATED = "escalated"

# Value Object
class SLADeadline(BaseModel):
    deadline: datetime
    severity: Severity

    @staticmethod
    def from_severity(severity: Severity, created_at: datetime) -> "SLADeadline":
        sla_hours = {
            Severity.CRITICAL: 1,
            Severity.HIGH: 4,
            Severity.MEDIUM: 24,
            Severity.LOW: 72
        }
        hours = sla_hours[severity]
        return SLADeadline(
            deadline=created_at + timedelta(hours=hours),
            severity=severity
        )

# Entitet — har unikt id og kan ændre tilstand
class Incident(BaseModel):
    incident_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    charger_id: str
    severity: Severity
    rule_name: str
    message: str
    value: float
    threshold: float
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: IncidentStatus = IncidentStatus.OPEN
    sla_deadline: SLADeadline = None
    assigned_technician_id: str = None
    events: list = Field(default_factory=list)

    model_config = {"arbitrary_types_allowed": True}

    def model_post_init(self, __context):
        if self.sla_deadline is None:
            object.__setattr__(self, 'sla_deadline',
                SLADeadline.from_severity(self.severity, self.timestamp))
        
        # Raise IncidentCreated event ved oprettelse
        self.events.append(IncidentCreated(
            incident_id=self.incident_id,
            charger_id=self.charger_id,
            severity=self.severity,
            rule_name=self.rule_name
        ))

    # Entitet metode — klassificér incident
    def classify(self, severity: Severity) -> None:
        self.severity = severity
        self.sla_deadline = SLADeadline.from_severity(severity, self.timestamp)
        self.events.append(IncidentClassified(
            incident_id=self.incident_id,
            severity=severity
        ))

    # Entitet metode — tildel tekniker
    def assign_technician(self, technician_id: str) -> None:
        if self.status == IncidentStatus.RESOLVED:
            raise ValueError(f"Incident {self.incident_id} er allerede løst")
        self.assigned_technician_id = technician_id
        self.status = IncidentStatus.ASSIGNED
        self.events.append(TechnicianAssignedToIncident(
            incident_id=self.incident_id,
            technician_id=technician_id
        ))

    # Entitet metode — eskalér incident
    def escalate(self) -> None:
        if self.status == IncidentStatus.RESOLVED:
            raise ValueError(f"Incident {self.incident_id} er allerede løst")
        self.status = IncidentStatus.ESCALATED
        self.events.append(IncidentEscalated(
            incident_id=self.incident_id,
            reason=f"Incident ikke løst inden SLA deadline {self.sla_deadline.deadline}"
        ))

    # Entitet metode — løs incident
    def resolve(self, resolved_by: str) -> None:
        self.status = IncidentStatus.RESOLVED
        self.events.append(IncidentResolved(
            incident_id=self.incident_id,
            resolved_by=resolved_by
        ))

    # Entitet metode — hent upublicerede events
    def pull_events(self) -> list:
        events = self.events.copy()
        self.events.clear()
        return events