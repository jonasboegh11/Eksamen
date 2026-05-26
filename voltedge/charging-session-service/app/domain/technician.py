from pydantic import BaseModel, Field
from datetime import datetime, timezone
from enum import Enum
import uuid

class TechnicianStatus(str, Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"

class TechnicianSpecialization(str, Enum):
    HARDWARE = "hardware"
    SOFTWARE = "software"
    NETWORK = "network"
    GENERAL = "general"

# Value Object
class ContactInfo(BaseModel):
    email: str
    phone: str

# Entitet — Technician
class Technician(BaseModel):
    technician_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    status: TechnicianStatus = TechnicianStatus.AVAILABLE
    specialization: TechnicianSpecialization = TechnicianSpecialization.GENERAL
    contact_info: ContactInfo = None
    assigned_incidents: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Entitet metode — tildel incident
    def assign_incident(self, incident_id: str) -> None:
        if self.status == TechnicianStatus.OFFLINE:
            raise ValueError(f"Tekniker {self.name} er offline og kan ikke tildeles incidents")
        self.assigned_incidents.append(incident_id)
        self.status = TechnicianStatus.BUSY

    # Entitet metode — løs incident
    def resolve_incident(self, incident_id: str) -> None:
        if incident_id not in self.assigned_incidents:
            raise ValueError(f"Incident {incident_id} er ikke tildelt tekniker {self.name}")
        self.assigned_incidents.remove(incident_id)
        if not self.assigned_incidents:
            self.status = TechnicianStatus.AVAILABLE

    # Entitet metode — sæt offline
    def go_offline(self) -> None:
        self.status = TechnicianStatus.OFFLINE

    # Entitet metode — sæt tilgængelig
    def go_available(self) -> None:
        self.status = TechnicianStatus.AVAILABLE