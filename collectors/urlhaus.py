import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime

from collectors.base_collector import BaseCollector
from collectors.utils.logger import logger

class URLHausCollector(BaseCollector):
    def __init__(self):
        super().__init__(
            source_name="URLHaus",
            source_type="Malicious URL Intelligence",
            trust_score=90
        )
        self.api_url = "https://urlhaus-api.abuse.ch/v1/urls/recent/"

    def fetch_data(self):
        response = self.fetch_api(self.api_url, method="GET")
        return response.json()

    def process_data(self, data):
        if data.get("query_status") != "ok":
            logger.error(f"[{self.source_name}] API returned non-ok status: {data.get('query_status')}")
            return 0, 0

        urls = data.get("urls", [])
        if not urls:
            return 0, 0

        conn = self.get_connection()
        cursor = conn.cursor()
        source_id = self.get_source_id(cursor)

        inserted = 0
        for item in urls:
            url_value = item.get("url")
            
            tags = item.get("tags")
            if tags is None:
                tags = []
            elif isinstance(tags, str):
                tags = [tags]

            cursor.execute(
                """
                INSERT INTO indicators
                (indicator_type, indicator_value, source_id, confidence, severity, tags, first_seen)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
                """,
                ("URL", url_value, source_id, 90, "High", tags, datetime.utcnow())
            )
            
            inserted += 1

        conn.commit()
        cursor.close()
        conn.close()

        return len(urls), inserted

def main():
    collector = URLHausCollector()
    collector.run()

if __name__ == "__main__":
    main()
