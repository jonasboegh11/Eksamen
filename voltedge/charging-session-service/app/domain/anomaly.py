from dataclasses import dataclass, field
from app.domain.telemetry import Telemetry
from app.domain.events import (
    AnomalyDetected,
    AnomalyClassified,
    ThresholdExceeded,
    AlarmTriggered
)
from app.domain.rule_engine import (
    POWER_CRITICAL_THRESHOLD,
    POWER_HIGH_THRESHOLD,
    POWER_MEDIUM_THRESHOLD,
    POWER_LOW_THRESHOLD,
    VOLTAGE_MIN,
    VOLTAGE_MAX,
    VOLTAGE_NOMINAL
)

# Value Object
@dataclass(frozen=True)
class AnomalyType:
    name: str
    description: str

# Value Object
@dataclass(frozen=True)
class Threshold:
    value: float
    unit: str

# Aggregat Rod — Anomaly
@dataclass
class Anomaly:
    charger_id: str
    anomaly_type: AnomalyType = None
    threshold: Threshold = None
    severity: str = None
    events: list = field(default_factory=list)

    def analyze(self, telemetry: Telemetry) -> list:
        self.events = []

        if telemetry.power_kw > POWER_CRITICAL_THRESHOLD:
            self._detect("power_critical", "Kritisk overbelastning", telemetry.power_kw, POWER_CRITICAL_THRESHOLD, "critical")
        elif telemetry.power_kw > POWER_HIGH_THRESHOLD:
            self._detect("power_high", "Høj belastning", telemetry.power_kw, POWER_HIGH_THRESHOLD, "high")
        elif telemetry.power_kw > POWER_MEDIUM_THRESHOLD:
            self._detect("power_medium", "Forhøjet belastning", telemetry.power_kw, POWER_MEDIUM_THRESHOLD, "medium")
        elif telemetry.power_kw > POWER_LOW_THRESHOLD:
            self._detect("power_low", "Usædvanlig belastning", telemetry.power_kw, POWER_LOW_THRESHOLD, "low")

        if telemetry.status.value == "faulted":
            self._detect("charger_faulted", "Lader rapporterer fejl", 0, 0, "high")
        elif telemetry.status.value == "offline":
            self._detect("charger_offline", "Lader er offline", 0, 0, "medium")

        if telemetry.voltage < VOLTAGE_MIN or telemetry.voltage > VOLTAGE_MAX:
            self._detect("voltage_abnormal", "Unormal spænding", telemetry.voltage, VOLTAGE_NOMINAL, "low")

        return self.events

    def _detect(self, rule_name: str, description: str, value: float, threshold_value: float, severity: str):
        self.anomaly_type = AnomalyType(name=rule_name, description=description)
        self.threshold = Threshold(value=threshold_value, unit="kW")
        self.severity = severity

        self.events.append(AnomalyDetected(
            charger_id=self.charger_id,
            anomaly_type=rule_name,
            value=value,
            threshold=threshold_value
        ))

        self.events.append(ThresholdExceeded(
            charger_id=self.charger_id,
            rule_name=rule_name,
            value=value,
            threshold=threshold_value
        ))

        self.events.append(AnomalyClassified(
            charger_id=self.charger_id,
            anomaly_type=rule_name,
            severity=severity
        ))

        self.events.append(AlarmTriggered(
            charger_id=self.charger_id,
            severity=severity,
            rule_name=rule_name,
            message=f"{description} på lader {self.charger_id}",
            value=value,
            threshold=threshold_value
        ))