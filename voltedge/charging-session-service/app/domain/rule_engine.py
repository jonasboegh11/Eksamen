from app.domain.telemetry import Telemetry
from app.domain.incident import Incident, Severity

# Tærskelværdier for belastning (kW)
POWER_CRITICAL_THRESHOLD = 50
POWER_HIGH_THRESHOLD = 22
POWER_MEDIUM_THRESHOLD = 11
POWER_LOW_THRESHOLD = 7

# Tærskelværdier for spænding (V)
VOLTAGE_MIN = 207
VOLTAGE_MAX = 253
VOLTAGE_NOMINAL = 230


def evaluate(telemetry: Telemetry) -> list[Incident]:
    incidents = []

    # Regel 1: Kritisk overbelastning (>50 kW)
    if telemetry.power_kw > POWER_CRITICAL_THRESHOLD:
        incidents.append(Incident(
            charger_id=telemetry.charger_id,
            severity=Severity.CRITICAL,
            rule_name="power_critical",
            message=f"Kritisk overbelastning på lader {telemetry.charger_id}",
            value=telemetry.power_kw,
            threshold=POWER_CRITICAL_THRESHOLD
        ))
    # Regel 2: Høj belastning (>22 kW)
    elif telemetry.power_kw > POWER_HIGH_THRESHOLD:
        incidents.append(Incident(
            charger_id=telemetry.charger_id,
            severity=Severity.HIGH,
            rule_name="power_high",
            message=f"Høj belastning på lader {telemetry.charger_id}",
            value=telemetry.power_kw,
            threshold=POWER_HIGH_THRESHOLD
        ))
    # Regel 3: Forhøjet belastning (>11 kW)
    elif telemetry.power_kw > POWER_MEDIUM_THRESHOLD:
        incidents.append(Incident(
            charger_id=telemetry.charger_id,
            severity=Severity.MEDIUM,
            rule_name="power_medium",
            message=f"Forhøjet belastning på lader {telemetry.charger_id}",
            value=telemetry.power_kw,
            threshold=POWER_MEDIUM_THRESHOLD
        ))
    # Regel 4: Lav men bemærkelsesværdig belastning (>7 kW)
    elif telemetry.power_kw > POWER_LOW_THRESHOLD:
        incidents.append(Incident(
            charger_id=telemetry.charger_id,
            severity=Severity.LOW,
            rule_name="power_low",
            message=f"Usædvanlig belastning på lader {telemetry.charger_id}",
            value=telemetry.power_kw,
            threshold=POWER_LOW_THRESHOLD
        ))

    # Regel 5: Lader er faulted
    if telemetry.status.value == "faulted":
        incidents.append(Incident(
            charger_id=telemetry.charger_id,
            severity=Severity.HIGH,
            rule_name="charger_faulted",
            message=f"Lader {telemetry.charger_id} rapporterer fejl",
            value=0,
            threshold=0
        ))

    # Regel 6: Lader er offline
    if telemetry.status.value == "offline":
        incidents.append(Incident(
            charger_id=telemetry.charger_id,
            severity=Severity.MEDIUM,
            rule_name="charger_offline",
            message=f"Lader {telemetry.charger_id} er offline",
            value=0,
            threshold=0
        ))

    # Regel 7: Unormal spænding
    if telemetry.voltage < VOLTAGE_MIN or telemetry.voltage > VOLTAGE_MAX:
        incidents.append(Incident(
            charger_id=telemetry.charger_id,
            severity=Severity.LOW,
            rule_name="voltage_abnormal",
            message=f"Unormal spænding på lader {telemetry.charger_id}",
            value=telemetry.voltage,
            threshold=VOLTAGE_NOMINAL
        ))

    return incidents