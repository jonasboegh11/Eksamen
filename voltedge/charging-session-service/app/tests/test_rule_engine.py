import pytest
from datetime import datetime
from app.domain.telemetry import Telemetry, ChargerStatus
from app.domain.incident import Severity
from app.domain.anomaly import Anomaly, POWER_CRITICAL_THRESHOLD
from app.domain.events import AlarmTriggered

def make_telemetry(power_kw=5.0, voltage=230.0, current=16.0, status="available"):
    return Telemetry(
        charger_id="TEST-001",
        status=ChargerStatus(status),
        power_kw=power_kw,
        voltage=voltage,
        current=current,
        timestamp=datetime.utcnow()
    )

def get_alarms(telemetry) -> list[AlarmTriggered]:
    anomaly = Anomaly(charger_id=telemetry.charger_id)
    events = anomaly.analyze(telemetry)
    return [e for e in events if isinstance(e, AlarmTriggered)]

# Ingen alarmer ved normal drift
def test_no_alarms_normal():
    telemetry = make_telemetry(power_kw=5.0, voltage=230.0)
    alarms = get_alarms(telemetry)
    assert len(alarms) == 0

# LOW alarm ved power > 7 kW
def test_low_alarm_power():
    telemetry = make_telemetry(power_kw=8.0)
    alarms = get_alarms(telemetry)
    assert len(alarms) == 1
    assert alarms[0].severity == "low"

# MEDIUM alarm ved power > 11 kW
def test_medium_alarm_power():
    telemetry = make_telemetry(power_kw=15.0)
    alarms = get_alarms(telemetry)
    assert len(alarms) == 1
    assert alarms[0].severity == "medium"

# HIGH alarm ved power > 22 kW
def test_high_alarm_power():
    telemetry = make_telemetry(power_kw=30.0)
    alarms = get_alarms(telemetry)
    assert len(alarms) == 1
    assert alarms[0].severity == "high"

# CRITICAL alarm ved power > 50 kW
def test_critical_alarm_power():
    telemetry = make_telemetry(power_kw=55.0)
    alarms = get_alarms(telemetry)
    assert len(alarms) == 1
    assert alarms[0].severity == "critical"

# HIGH alarm ved faulted status
def test_high_alarm_faulted():
    telemetry = make_telemetry(status="faulted")
    alarms = get_alarms(telemetry)
    assert any(a.rule_name == "charger_faulted" for a in alarms)
    assert any(a.severity == "high" for a in alarms)

# MEDIUM alarm ved offline status
def test_medium_alarm_offline():
    telemetry = make_telemetry(status="offline")
    alarms = get_alarms(telemetry)
    assert any(a.rule_name == "charger_offline" for a in alarms)
    assert any(a.severity == "medium" for a in alarms)

# LOW alarm ved unormal spænding
def test_low_alarm_voltage():
    telemetry = make_telemetry(voltage=200.0)
    alarms = get_alarms(telemetry)
    assert any(a.rule_name == "voltage_abnormal" for a in alarms)

# To alarmer ved faulted + høj belastning
def test_multiple_alarms():
    telemetry = make_telemetry(power_kw=8.0, status="faulted")
    alarms = get_alarms(telemetry)
    assert len(alarms) == 2

# Korrekte værdier på alarm
def test_alarm_values():
    telemetry = make_telemetry(power_kw=55.0)
    alarms = get_alarms(telemetry)
    assert alarms[0].value == 55.0
    assert alarms[0].threshold == POWER_CRITICAL_THRESHOLD