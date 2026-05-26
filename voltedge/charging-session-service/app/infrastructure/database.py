import mysql.connector.pooling
import os
import logging

logger = logging.getLogger("voltedge.charging-session")

_pool = None

def get_pool():
    global _pool
    if _pool is None:
        _pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="voltedge_pool",
            pool_size=10,
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", 3306)),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        logger.info("Database connection pool oprettet (pool_size=10)")
    return _pool

def get_connection():
    return get_pool().get_connection()

def init_db():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS incidents (
                id INT AUTO_INCREMENT PRIMARY KEY,
                incident_id VARCHAR(36) NOT NULL,
                charger_id VARCHAR(50) NOT NULL,
                severity VARCHAR(20) NOT NULL,
                rule_name VARCHAR(50) NOT NULL,
                message TEXT NOT NULL,
                value FLOAT NOT NULL,
                threshold FLOAT NOT NULL,
                timestamp DATETIME NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'open',
                sla_deadline DATETIME
            )
        """)

        conn.commit()
        cursor.close()
        conn.close()
        logger.info("Database initialiseret — incidents tabel klar")

    except mysql.connector.Error as e:
        logger.critical(f"Kunne ikke initialisere database: {e}")
        raise RuntimeError(f"Database initialisering fejlede: {e}") from e