import sys
import os
sys.path.append(r"D:\Repos\Silentwatch_CTIP")
from dotenv import load_dotenv
load_dotenv()
from collectors.utils.database import get_connection

conn = get_connection()
cursor = conn.cursor()
try:
    cursor.execute("""
    ALTER TABLE vulnerabilities
    ADD COLUMN IF NOT EXISTS attack_vector VARCHAR(50),
    ADD COLUMN IF NOT EXISTS attack_complexity VARCHAR(50),
    ADD COLUMN IF NOT EXISTS privileges_required VARCHAR(50),
    ADD COLUMN IF NOT EXISTS user_interaction VARCHAR(50),
    ADD COLUMN IF NOT EXISTS cwe VARCHAR(50);
    """)
    conn.commit()
    print("Columns added successfully")
except Exception as e:
    print("Error:", e)
finally:
    cursor.close()
    conn.close()
