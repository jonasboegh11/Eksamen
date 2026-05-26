from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class ChargerStatus(str, Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    FAULTED = "faulted"
    OFFLINE = "offline"

# Value Object — ingen unik identitet, to ens målinger er identiske
class MeasurementValue(BaseModel):
    power_kw: float
    voltage: float
    current: float

    class Config:
        frozen = True  # Value objects er immutable

    def is_overloaded(self) -> bool:
        return self.power_kw > 50

    def is_voltage_abnormal(self) -> bool:
        return self.voltage < 207 or self.voltage > 253

# Value Object — repræsenterer en telemetri-strøm fra en lader
class TelemetryStream(BaseModel):
    charger_id: str
    status: ChargerStatus
    measurement: MeasurementValue
    timestamp: datetime = None

    class Config:
        frozen = True  # Value objects er immutable

    def __init__(self, **data):
        if not data.get("timestamp"):
            data["timestamp"] = datetime.utcnow()
        super().__init__(**data)

# Bagudkompatibilitet — så eksisterende kode stadig virker
class Telemetry(BaseModel):
    charger_id: str
    status: ChargerStatus
    power_kw: float
    voltage: float
    current: float
    timestamp: datetime = None

    def __init__(self, **data):
        if not data.get("timestamp"):
            data["timestamp"] = datetime.utcnow()
        super().__init__(**data)

    def to_stream(self) -> TelemetryStream:
        return TelemetryStream(
            charger_id=self.charger_id,
            status=self.status,
            measurement=MeasurementValue(
                power_kw=self.power_kw,
                voltage=self.voltage,
                current=self.current
            ),
            timestamp=self.timestamp
        )