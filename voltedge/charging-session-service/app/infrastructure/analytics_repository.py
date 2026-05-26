import logging
from app.infrastructure.database import get_connection

logger = logging.getLogger("voltedge.charging-session")

class AnalyticsRepository:

    def get_incidents_per_severity(self) -> list[dict]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT severity, COUNT(*) as count
            FROM incidents
            GROUP BY severity
            ORDER BY FIELD(severity, 'critical', 'high', 'medium', 'low')
        """)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results

    def get_incidents_per_charger(self) -> list[dict]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT charger_id, COUNT(*) as count,
                   MAX(timestamp) as latest_incident
            FROM incidents
            GROUP BY charger_id
            ORDER BY count DESC
        """)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results

    def get_most_problematic_charger(self) -> dict | None:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT charger_id, COUNT(*) as incident_count,
                   MAX(timestamp) as latest_incident,
                   SUM(CASE WHEN severity = 'critical' THEN 1 ELSE 0 END) as critical_count,
                   SUM(CASE WHEN severity = 'high' THEN 1 ELSE 0 END) as high_count
            FROM incidents
            GROUP BY charger_id
            ORDER BY incident_count DESC
            LIMIT 1
        """)
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result

    def get_summary(self) -> dict:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                COUNT(*) as total_incidents,
                SUM(CASE WHEN severity = 'critical' THEN 1 ELSE 0 END) as critical,
                SUM(CASE WHEN severity = 'high' THEN 1 ELSE 0 END) as high,
                SUM(CASE WHEN severity = 'medium' THEN 1 ELSE 0 END) as medium,
                SUM(CASE WHEN severity = 'low' THEN 1 ELSE 0 END) as low,
                COUNT(DISTINCT charger_id) as affected_chargers,
                MAX(timestamp) as latest_incident
            FROM incidents
        """)
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result

    def get_incidents_last_24h(self, charger_id: str) -> dict:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN severity = 'critical' THEN 1 ELSE 0 END) as critical_count,
                SUM(CASE WHEN severity = 'high' THEN 1 ELSE 0 END) as high_count,
                AVG(value) as avg_value
            FROM incidents
            WHERE charger_id = %s
            AND timestamp >= NOW() - INTERVAL 24 HOUR
        """, (charger_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result