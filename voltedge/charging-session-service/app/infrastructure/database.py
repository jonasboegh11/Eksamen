import mysql.connector
import os
import logging

logger = logging.getLogger("voltedge.charging-session")

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 3306)),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id INT AUTO_INCREMENT PRIMARY KEY,
            charger_id VARCHAR(50) NOT NULL,
            severity VARCHAR(20) NOT NULL,
            rule_name VARCHAR(50) NOT NULL,
            message TEXT NOT NULL,
            value FLOAT NOT NULL,
            threshold FLOAT NOT NULL,
            timestamp DATETIME NOT NULL
        )
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    logger.info("Database initialiseret — incidents tabel klar")