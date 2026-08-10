import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collectors.base_collector import BaseCollector
from collectors.utils.logger import logger

CISA_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"

class CISAKEVCollector(BaseCollector):
    def __init__(self):
        super().__init__(
            source_name="CISA KEV",
            source_type="Vulnerability Intelligence",
            trust_score=100
        )
        self.api_url = CISA_URL

    def fetch_data(self):
        logger.info("Fetching CISA KEV catalog")
        # Leveraging the BaseCollector's fetch_api for automatic retries and standard session handling
        response = self.fetch_api(self.api_url, method="GET")
        return response.json()

    def process_data(self, data):
        vulns = data.get("vulnerabilities", [])
        if not vulns:
            return 0, 0

        conn = self.get_connection()
        cursor = conn.cursor()
        source_id = self.get_source_id(cursor)

        inserted = 0
        for item in vulns:
            cve_id = item.get("cveID")
            vendor = item.get("vendorProject")
            product = item.get("product")
            name = item.get("vulnerabilityName")
            description = item.get("shortDescription")
            date_added = item.get("dateAdded")
            
            # The API returns "Known" or "Unknown" for ransomware campaign use
            ransomware_use_raw = item.get("knownRansomwareCampaignUse", "Unknown")
            ransomware_use = (ransomware_use_raw.lower() == "known")

            # 1. Insert into vulnerabilities (has a UNIQUE constraint on cve_id)
            cursor.execute(
                """
                INSERT INTO vulnerabilities
                (cve_id, title, description, vendor, product, published_date, source_id)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (cve_id) DO NOTHING
                """,
                (cve_id, name, description, vendor, product, date_added, source_id)
            )
            
            # Increment inserted counter only if a new row was added to vulnerabilities
            if cursor.rowcount:
                inserted += 1
            
            # 2. Insert into exploited_vulnerabilities 
            # (No unique constraint exists, so we check first to avoid duplicates)
            cursor.execute("SELECT 1 FROM exploited_vulnerabilities WHERE cve_id=%s", (cve_id,))
            if not cursor.fetchone():
                cursor.execute(
                    """
                    INSERT INTO exploited_vulnerabilities
                    (cve_id, vendor, product, date_added, ransomware_use)
                    VALUES (%s,%s,%s,%s,%s)
                    """,
                    (cve_id, vendor, product, date_added, ransomware_use)
                )

        conn.commit()
        cursor.close()
        conn.close()

        return len(vulns), inserted

def main():
    collector = CISAKEVCollector()
    collector.run()

if __name__ == "__main__":
    main()
