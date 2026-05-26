from dataclasses import dataclass, field
from datetime import datetime
from app.domain.telemetry import Telemetry
from app.domain.incident import Incident, Severity

# Value Object
@dataclass(frozen=True)
class MeasurementValue:
    power_kw: float
    voltage: float
    current: float
    timestamp: datetime

# Aggregat Rod — ChargerDevice
@dataclass
class ChargerDevice:
    charger_id: str
    status: str
    telemetry_stream: list[MeasurementValue] = field(default_factory=list)
    incidents: list[Incident] = field(default_factory=list)

    # Aggregat metode — modtag telemetri
    def receive_telemetry(self, telemetry: Telemetry) -> list[Incident]:
        measurement = MeasurementValue(
            power_kw=telemetry.power_kw,
            voltage=telemetry.voltage,
            current=telemetry.current,
            timestamp=telemetry.timestamp
        )
        self.telemetry_stream.append(measurement)
        self.status = telemetry.status.value
        return measurement

    # Aggregat metode — tilføj incident
    def add_incident(self, incident: Incident):
        self.incidents.append(incident)

    # Aggregat metode — hent seneste måling
    def latest_measurement(self) -> MeasurementValue | None:
        if self.telemetry_stream:
            return self.telemetry_stream[-1]
        return None

    # Aggregat metode — har aktive incidents
    def has_critical_incidents(self) -> bool:
        return any(i.severity == Severity.CRITICAL for i in self.incidents)