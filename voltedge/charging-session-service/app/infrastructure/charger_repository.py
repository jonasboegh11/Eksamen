import logging
from app.infrastructure.database import get_connection

logger = logging.getLogger("voltedge.charging-session")

class ChargerRepository:

    def get_open_incident_count(self, charger_id: str) -> int:
        """Henter antal åbne incidents for en lader fra databasen."""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM incidents
            WHERE charger_id = %s
            AND status = 'open'
        """, (charger_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result["count"] if result else 0

    def has_critical_incidents(self, charger_id: str) -> bool:
        """Tjekker om en lader har åbne kritiske incidents i databasen."""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM incidents
            WHERE charger_id = %s
            AND severity = 'critical'
            AND status = 'open'
        """, (charger_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result["count"] > 0 if result else False