import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)

# ─── Health ───────────────────────────────────────────────────────────────────

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

# ─── Telemetri ────────────────────────────────────────────────────────────────

@patch("app.api.telemetry_router.repository")
@patch("app.api.telemetry_router.charger_repository")
def test_telemetry_normal(mock_charger_repo, mock_incident_repo):
    mock_charger_repo.has_critical_incidents.return_value = False
    mock_incident_repo.save.return_value = None

    response = client.post("/telemetry/", json={
        "charger_id": "TEST-001",
        "status": "available",
        "power_kw": 3.0,
        "voltage": 230.0,
        "current": 16.0
    })

    assert response.status_code == 200
    data = response.json()
    assert data["charger_id"] == "TEST-001"
    assert data["incidents_count"] == 0
    assert data["has_critical_incidents"] == False

@patch("app.api.telemetry_router.repository")
@patch("app.api.telemetry_router.charger_repository")
def test_telemetry_critical_power(mock_charger_repo, mock_incident_repo):
    mock_charger_repo.has_critical_incidents.return_value = False
    mock_incident_repo.save.return_value = None

    response = client.post("/telemetry/", json={
        "charger_id": "TEST-001",
        "status": "occupied",
        "power_kw": 55.0,
        "voltage": 230.0,
        "current": 16.0
    })

    assert response.status_code == 200
    data = response.json()
    assert data["incidents_count"] == 1
    assert data["incidents"][0]["severity"] == "critical"
    assert data["incidents"][0]["rule_name"] == "power_critical"
    assert data["has_critical_incidents"] == True

@patch("app.api.telemetry_router.repository")
@patch("app.api.telemetry_router.charger_repository")
def test_telemetry_faulted_charger(mock_charger_repo, mock_incident_repo):
    mock_charger_repo.has_critical_incidents.return_value = False
    mock_incident_repo.save.return_value = None

    response = client.post("/telemetry/", json={
        "charger_id": "TEST-002",
        "status": "faulted",
        "power_kw": 3.0,
        "voltage": 230.0,
        "current": 16.0
    })

    assert response.status_code == 200
    data = response.json()
    assert data["incidents_count"] == 1
    assert data["incidents"][0]["severity"] == "high"
    assert data["incidents"][0]["rule_name"] == "charger_faulted"

@patch("app.api.telemetry_router.repository")
@patch("app.api.telemetry_router.charger_repository")
def test_telemetry_invalid_power(mock_charger_repo, mock_incident_repo):
    mock_charger_repo.has_critical_incidents.return_value = False

    response = client.post("/telemetry/", json={
        "charger_id": "TEST-001",
        "status": "available",
        "power_kw": -10.0,
        "voltage": 230.0,
        "current": 16.0
    })

    assert response.status_code == 422

@patch("app.api.telemetry_router.repository")
@patch("app.api.telemetry_router.charger_repository")
def test_telemetry_persisted_critical_state(mock_charger_repo, mock_incident_repo):
    """Verificerer at has_critical_incidents hentes fra db selv uden nye incidents."""
    mock_charger_repo.has_critical_incidents.return_value = True
    mock_incident_repo.save.return_value = None

    response = client.post("/telemetry/", json={
        "charger_id": "TEST-001",
        "status": "available",
        "power_kw": 3.0,
        "voltage": 230.0,
        "current": 16.0
    })

    assert response.status_code == 200
    data = response.json()
    assert data["incidents_count"] == 0
    assert data["has_critical_incidents"] == True

# ─── Incidents ────────────────────────────────────────────────────────────────

@patch("app.api.incident_router.repository")
def test_get_incidents(mock_repo):
    mock_repo.get_all.return_value = [
        {
            "id": 1,
            "incident_id": "abc-123",
            "charger_id": "TEST-001",
            "severity": "critical",
            "rule_name": "power_critical",
            "message": "Kritisk overbelastning",
            "value": 55.0,
            "threshold": 50.0,
            "timestamp": "2026-01-01T00:00:00",
            "status": "open",
            "sla_deadline": "2026-01-01T01:00:00"
        }
    ]

    response = client.get("/incidents/")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
    assert data["incidents"][0]["severity"] == "critical"

@patch("app.api.incident_router.repository")
def test_get_incident_not_found(mock_repo):
    mock_repo.get_by_id.return_value = None

    response = client.get("/incidents/999")
    assert response.status_code == 404

# ─── Analytics ────────────────────────────────────────────────────────────────

@patch("app.api.analytics_router.repository")
def test_analytics_summary(mock_repo):
    mock_repo.get_summary.return_value = {
        "total_incidents": 5,
        "critical": 2,
        "high": 1,
        "medium": 1,
        "low": 1,
        "affected_chargers": 2,
        "latest_incident": "2026-01-01T00:00:00"
    }

    response = client.get("/analytics/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["summary"]["total_incidents"] == 5
    assert data["summary"]["critical"] == 2

@patch("app.api.analytics_router.repository")
@patch("app.api.analytics_router.prediction_service")
def test_analytics_predict(mock_prediction, mock_repo):
    from datetime import datetime, timezone
    from app.domain.prediction_service import PredictionResult

    mock_repo.get_incidents_last_24h.return_value = {
        "total": 5,
        "critical_count": 3,
        "high_count": 1,
        "avg_value": 55.0
    }
    mock_prediction.predict.return_value = PredictionResult(
        charger_id="TEST-001",
        risk_score=0.95,
        risk_level="critical",
        recommendation="Lader TEST-001 kræver øjeblikkelig inspektion",
        based_on_incidents=5,
        predicted_at=datetime.now(timezone.utc)
    )

    response = client.get("/analytics/predict/TEST-001")
    assert response.status_code == 200
    data = response.json()
    assert data["risk_level"] == "critical"
    assert data["risk_score"] == 0.95