from pydantic import BaseModel, Field
from datetime import datetime, timezone
from enum import Enum
import uuid

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
        from datetime import timedelta
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

    def model_post_init(self, __context):
        if self.sla_deadline is None:
            object.__setattr__(self, 'sla_deadline',
                SLADeadline.from_severity(self.severity, self.timestamp))

    # Entitet metode — eskalér incident
    def escalate(self):
        return Incident(
            incident_id=self.incident_id,
            charger_id=self.charger_id,
            severity=self.severity,
            rule_name=self.rule_name,
            message=self.message,
            value=self.value,
            threshold=self.threshold,
            timestamp=self.timestamp,
            status=IncidentStatus.ESCALATED,
            sla_deadline=self.sla_deadline
        )

    # Entitet metode — løs incident
    def resolve(self):
        return Incident(
            incident_id=self.incident_id,
            charger_id=self.charger_id,
            severity=self.severity,
            rule_name=self.rule_name,
            message=self.message,
            value=self.value,
            threshold=self.threshold,
            timestamp=self.timestamp,
            status=IncidentStatus.RESOLVED,
            sla_deadline=self.sla_deadline
        )