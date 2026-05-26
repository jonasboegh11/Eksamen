from pydantic import BaseModel
from pydantic import ConfigDict
from datetime import datetime
from enum import Enum

class ChargerStatus(str, Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    FAULTED = "faulted"
    OFFLINE = "offline"

# Value Object
class MeasurementValue(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    power_kw: float
    voltage: float
    current: float

    def is_overloaded(self) -> bool:
        return self.power_kw > 50

    def is_voltage_abnormal(self) -> bool:
        return self.voltage < 207 or self.voltage > 253

# Value Object
class TelemetryStream(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    charger_id: str
    status: ChargerStatus
    measurement: MeasurementValue
    timestamp: datetime = None

    def __init__(self, **data):
        if not data.get("timestamp"):
            data["timestamp"] = datetime.utcnow()
        super().__init__(**data)

# Bagudkompatibilitet
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