import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from collectors.utils.database import get_connection
from collectors.utils.logger import logger

def log_feed_run(received: int, processed: int, status: str):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO feed_history (records_received, records_processed, status) 
            VALUES (%s, %s, %s)
            """,
            (received, processed, status)
        )
        conn.commit()
    except Exception as e:
        logger.error(f"Error logging feed history: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
