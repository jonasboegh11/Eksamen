from dataclasses import dataclass, field
from app.domain.telemetry import Telemetry, MeasurementValue
from app.domain.incident import Incident, Severity

# Aggregat Rod — ChargerDevice
@dataclass
class ChargerDevice:
    charger_id: str
    status: str
    telemetry_stream: list[MeasurementValue] = field(default_factory=list)
    incidents: list[Incident] = field(default_factory=list)
    _has_critical_from_db: bool = False

    # Aggregat metode — modtag telemetri
    def receive_telemetry(self, telemetry: Telemetry) -> MeasurementValue:
        measurement = MeasurementValue(
            power_kw=telemetry.power_kw,
            voltage=telemetry.voltage,
            current=telemetry.current
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

    # Aggregat metode — sæt persisteret kritisk status
    def set_critical_from_db(self, has_critical: bool):
        self._has_critical_from_db = has_critical

    # Aggregat metode — har aktive kritiske incidents (in-memory + db)
    def has_critical_incidents(self) -> bool:
        in_memory = any(i.severity == Severity.CRITICAL for i in self.incidents)
        return in_memory or self._has_critical_from_db