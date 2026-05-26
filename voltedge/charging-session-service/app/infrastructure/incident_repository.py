import logging
from app.infrastructure.database import get_connection
from app.domain.incident import Incident

logger = logging.getLogger("voltedge.charging-session")

class IncidentRepository:

    def save(self, incident: Incident) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO incidents (incident_id, charger_id, severity, rule_name, message, value, threshold, timestamp, status, sla_deadline)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            incident.incident_id,
            incident.charger_id,
            incident.severity,
            incident.rule_name,
            incident.message,
            incident.value,
            incident.threshold,
            incident.timestamp,
            incident.status,
            incident.sla_deadline.deadline
        ))
        conn.commit()
        cursor.close()
        conn.close()

    def get_all(self, severity: str = None, charger_id: str = None) -> list[dict]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM incidents WHERE 1=1"
        params = []

        if severity:
            query += " AND severity = %s"
            params.append(severity)

        if charger_id:
            query += " AND charger_id = %s"
            params.append(charger_id)

        query += " ORDER BY timestamp DESC"

        cursor.execute(query, params)
        incidents = cursor.fetchall()
        cursor.close()
        conn.close()
        return incidents

    def get_by_id(self, incident_id: int) -> dict | None:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM incidents WHERE id = %s", (incident_id,))
        incident = cursor.fetchone()
        cursor.close()
        conn.close()
        return incident