import pytest
from datetime import datetime
from app.domain.telemetry import Telemetry, ChargerStatus
from app.domain.incident import Severity
from app.domain.rule_engine import evaluate

def make_telemetry(power_kw=5.0, voltage=230.0, current=16.0, status="available"):
    return Telemetry(
        charger_id="TEST-001",
        status=ChargerStatus(status),
        power_kw=power_kw,
        voltage=voltage,
        current=current,
        timestamp=datetime.utcnow()
    )

# Ingen incidents ved normal drift
def test_no_incidents_normal():
    telemetry = make_telemetry(power_kw=5.0, voltage=230.0)
    incidents = evaluate(telemetry)
    assert len(incidents) == 0

# LOW incident ved power > 7 kW
def test_low_incident_power():
    telemetry = make_telemetry(power_kw=8.0)
    incidents = evaluate(telemetry)
    assert len(incidents) == 1
    assert incidents[0].severity == Severity.LOW

# MEDIUM incident ved power > 11 kW
def test_medium_incident_power():
    telemetry = make_telemetry(power_kw=15.0)
    incidents = evaluate(telemetry)
    assert len(incidents) == 1
    assert incidents[0].severity == Severity.MEDIUM

# HIGH incident ved power > 22 kW
def test_high_incident_power():
    telemetry = make_telemetry(power_kw=30.0)
    incidents = evaluate(telemetry)
    assert len(incidents) == 1
    assert incidents[0].severity == Severity.HIGH

# CRITICAL incident ved power > 50 kW
def test_critical_incident_power():
    telemetry = make_telemetry(power_kw=55.0)
    incidents = evaluate(telemetry)
    assert len(incidents) == 1
    assert incidents[0].severity == Severity.CRITICAL

# HIGH incident ved faulted status
def test_high_incident_faulted():
    telemetry = make_telemetry(status="faulted")
    incidents = evaluate(telemetry)
    assert any(i.rule_name == "charger_faulted" for i in incidents)
    assert any(i.severity == Severity.HIGH for i in incidents)

# MEDIUM incident ved offline status
def test_medium_incident_offline():
    telemetry = make_telemetry(status="offline")
    incidents = evaluate(telemetry)
    assert any(i.rule_name == "charger_offline" for i in incidents)
    assert any(i.severity == Severity.MEDIUM for i in incidents)

# LOW incident ved unormal spænding
def test_low_incident_voltage():
    telemetry = make_telemetry(voltage=200.0)
    incidents = evaluate(telemetry)
    assert any(i.rule_name == "voltage_abnormal" for i in incidents)

# To incidents ved faulted + høj belastning
def test_multiple_incidents():
    telemetry = make_telemetry(power_kw=8.0, status="faulted")
    incidents = evaluate(telemetry)
    assert len(incidents) == 2

# SLA deadline sættes korrekt
def test_sla_deadline_critical():
    telemetry = make_telemetry(power_kw=55.0)
    incidents = evaluate(telemetry)
    assert incidents[0].sla_deadline is not None
    diff = incidents[0].sla_deadline.deadline - incidents[0].timestamp
    assert diff.seconds == 3600  # 1 time = 3600 sekunder