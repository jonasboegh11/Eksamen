from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class ChargerStatus(str, Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    FAULTED = "faulted"
    OFFLINE = "offline"

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