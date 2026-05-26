from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime, timezone
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

    @field_validator("power_kw")
    @classmethod
    def validate_power(cls, v):
        if v < 0:
            raise ValueError(f"power_kw må ikke være negativ, fik {v}")
        if v > 350:
            raise ValueError(f"power_kw overskrider maksimum (350 kW), fik {v}")
        return v

    @field_validator("voltage")
    @classmethod
    def validate_voltage(cls, v):
        if v < 0:
            raise ValueError(f"voltage må ikke være negativ, fik {v}")
        if v > 1000:
            raise ValueError(f"voltage overskrider maksimum (1000 V), fik {v}")
        return v

    @field_validator("current")
    @classmethod
    def validate_current(cls, v):
        if v < 0:
            raise ValueError(f"current må ikke være negativ, fik {v}")
        if v > 630:
            raise ValueError(f"current overskrider maksimum (630 A), fik {v}")
        return v

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
            data["timestamp"] = datetime.now(timezone.utc)
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
            data["timestamp"] = datetime.now(timezone.utc)
        super().__init__(**data)

    @field_validator("power_kw")
    @classmethod
    def validate_power(cls, v):
        if v < 0:
            raise ValueError(f"power_kw må ikke være negativ, fik {v}")
        if v > 350:
            raise ValueError(f"power_kw overskrider maksimum (350 kW), fik {v}")
        return v

    @field_validator("voltage")
    @classmethod
    def validate_voltage(cls, v):
        if v < 0:
            raise ValueError(f"voltage må ikke være negativ, fik {v}")
        if v > 1000:
            raise ValueError(f"voltage overskrider maksimum (1000 V), fik {v}")
        return v

    @field_validator("current")
    @classmethod
    def validate_current(cls, v):
        if v < 0:
            raise ValueError(f"current må ikke være negativ, fik {v}")
        if v > 630:
            raise ValueError(f"current overskrider maksimum (630 A), fik {v}")
        return v

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