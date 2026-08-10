import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from dotenv import load_dotenv

from collectors.base_collector import BaseCollector
from collectors.utils.logger import logger

load_dotenv()

class OTXCollector(BaseCollector):
    def __init__(self):
        super().__init__(
            source_name="AlienVault OTX",
            source_type="Threat Intelligence Platform",
            trust_score=80
        )
        self.api_url = "https://otx.alienvault.com/api/v1/pulses/subscribed"
        self.api_key = os.getenv("OTX_API_KEY")

    def fetch_data(self):
        if not self.api_key:
            raise ValueError("OTX_API_KEY environment variable not set. Please add it to your .env file.")
            
        headers = {
            "X-OTX-API-KEY": self.api_key
        }
        response = self.fetch_api(self.api_url, method="GET", headers=headers)
        return response.json()

    def process_data(self, data):
        pulses = data.get("results", [])
        if not pulses:
            return 0, 0

        conn = self.get_connection()
        cursor = conn.cursor()
        source_id = self.get_source_id(cursor)

        inserted = 0
        total_indicators = 0
        
        for pulse in pulses:
            indicators = pulse.get("indicators", [])
            tags = pulse.get("tags", [])
            if tags is None:
                tags = []
                
            for ind in indicators:
                total_indicators += 1
                ind_type = ind.get("type", "Unknown")
                ind_value = ind.get("indicator")
                
                # Normalize types to be cleaner in the database based on prompt examples
                if "IP" in ind_type:
                    ind_type = "IP"
                elif "domain" in ind_type.lower():
                    ind_type = "Domain"
                elif "hash" in ind_type.lower() or "md5" in ind_type.lower() or "sha" in ind_type.lower():
                    ind_type = "Hash"

                cursor.execute(
                    """
                    INSERT INTO indicators
                    (indicator_type, indicator_value, source_id, confidence, severity, tags, first_seen)
                    VALUES (%s,%s,%s,%s,%s,%s,%s)
                    """,
                    (ind_type, ind_value, source_id, 80, "High", tags, datetime.utcnow())
                )
                
                inserted += 1

        conn.commit()
        cursor.close()
        conn.close()

        return total_indicators, inserted

def main():
    collector = OTXCollector()
    collector.run()

if __name__ == "__main__":
    main()
