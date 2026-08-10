import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from collectors.utils.database import get_connection
from collectors.utils.logger import logger
from collectors.utils.feed_logger import log_feed_run

class BaseCollector:
    def __init__(self, source_name: str, source_type: str, trust_score: int):
        self.source_name = source_name
        self.source_type = source_type
        self.trust_score = trust_score

    def fetch_api(self, url: str, method: str = "GET", headers: dict = None, data: dict = None, params: dict = None, timeout: int = 30, retries: int = 3):
        """Fetches data from an API with automatic retries on connection failures or 5xx errors."""
        session = requests.Session()
        retry_strategy = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        try:
            response = session.request(
                method=method,
                url=url,
                headers=headers,
                data=data,
                params=params,
                timeout=timeout
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"[{self.source_name}] API Request Failed: {e}")
            raise

    def get_source_id(self, cursor) -> int:
        """Retrieves or creates the source record in the intel_sources table."""
        cursor.execute("SELECT id FROM intel_sources WHERE name=%s", (self.source_name,))
        result = cursor.fetchone()
        if result:
            return result[0]
            
        cursor.execute(
            """
            INSERT INTO intel_sources (name, source_type, trust_score) 
            VALUES (%s, %s, %s) RETURNING id
            """,
            (self.source_name, self.source_type, self.trust_score)
        )
        return cursor.fetchone()[0]
        
    def get_connection(self):
        """Provides a database connection."""
        return get_connection()

    def fetch_data(self):
        """Abstract method to fetch data from the provider. Must be implemented by child class."""
        raise NotImplementedError("Child class must implement fetch_data")

    def process_data(self, data) -> tuple[int, int]:
        """Abstract method to process data and save to DB. Must be implemented by child class.
        Returns: (records_received, records_processed)
        """
        raise NotImplementedError("Child class must implement process_data")

    def run(self):
        """The main execution loop for the collector."""
        logger.info(f"Starting {self.source_name} collector")
        received = 0
        processed = 0
        status = "failed"
        try:
            data = self.fetch_data()
            received, processed = self.process_data(data)
            status = "success"
            logger.info(f"[{self.source_name}] Successfully received {received} and inserted {processed} records.")
        except Exception as e:
            logger.error(f"[{self.source_name}] Collector execution failed: {e}")
        finally:
            log_feed_run(received, processed, status)
