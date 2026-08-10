import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

from collectors.base_collector import BaseCollector
from collectors.utils.logger import logger
from collectors.utils.feed_logger import log_feed_run

load_dotenv()

class NVDCollector(BaseCollector):
    def __init__(self):
        super().__init__(
            source_name="NVD",
            source_type="Vulnerability Enrichment",
            trust_score=100
        )
        self.api_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
        self.api_key = os.getenv("NVD_API_KEY")

    def fetch_data(self):
        # NVD fetches per-CVE, so we bypass the standard bulk fetch 
        pass

    def process_data(self, data):
        pass

    def run(self):
        """Override the standard run loop for per-CVE enrichment"""
        logger.info(f"Starting {self.source_name} collector")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # We select CVEs that haven't been enriched yet (cvss_score is NULL)
        cursor.execute("SELECT id, cve_id FROM vulnerabilities WHERE cvss_score IS NULL")
        cves_to_enrich = cursor.fetchall()
        
        if not cves_to_enrich:
            logger.info(f"[{self.source_name}] No CVEs found needing enrichment.")
            cursor.close()
            conn.close()
            return

        headers = {}
        if self.api_key:
            headers["apiKey"] = self.api_key
        else:
            logger.warning(f"[{self.source_name}] No NVD_API_KEY found. Requests will be severely rate-limited.")

        processed = 0
        status = "failed"
        
        try:
            for row_id, cve_id in cves_to_enrich:
                params = {"cveId": cve_id}
                try:
                    # Using the built-in fetch_api which has retries
                    response = self.fetch_api(self.api_url, method="GET", headers=headers, params=params)
                    cve_data = response.json()
                    
                    vulnerabilities = cve_data.get("vulnerabilities", [])
                    if not vulnerabilities:
                        continue
                        
                    cve_item = vulnerabilities[0].get("cve", {})
                    metrics = cve_item.get("metrics", {})
                    
                    # Extract CVSS v3.1 or v3.0 metrics
                    cvss_data = None
                    if "cvssMetricV31" in metrics:
                        cvss_data = metrics["cvssMetricV31"][0].get("cvssData", {})
                    elif "cvssMetricV30" in metrics:
                        cvss_data = metrics["cvssMetricV30"][0].get("cvssData", {})
                    
                    cvss_score = None
                    severity = None
                    attack_vector = None
                    attack_complexity = None
                    privileges_required = None
                    user_interaction = None
                    cwe = None
                    
                    if cvss_data:
                        cvss_score = cvss_data.get("baseScore")
                        severity = cvss_data.get("baseSeverity")
                        attack_vector = cvss_data.get("attackVector")
                        attack_complexity = cvss_data.get("attackComplexity")
                        privileges_required = cvss_data.get("privilegesRequired")
                        user_interaction = cvss_data.get("userInteraction")
                        
                    weaknesses = cve_item.get("weaknesses", [])
                    if weaknesses:
                        cwe_desc = weaknesses[0].get("description", [])
                        if cwe_desc:
                            cwe = cwe_desc[0].get("value")
                            
                    cursor.execute(
                        """
                        UPDATE vulnerabilities
                        SET cvss_score=%s, severity=%s, attack_vector=%s, attack_complexity=%s, 
                            privileges_required=%s, user_interaction=%s, cwe=%s
                        WHERE id=%s
                        """,
                        (cvss_score, severity, attack_vector, attack_complexity, privileges_required, user_interaction, cwe, row_id)
                    )
                    conn.commit()
                    processed += 1
                    
                    if processed % 50 == 0:
                        logger.info(f"[{self.source_name}] Progress: Enriched {processed}/{len(cves_to_enrich)} CVEs...")
                    
                    # Respect NVD Rate limits (50 req/30s with API key, 5 req/30s without)
                    time.sleep(1 if self.api_key else 6)

                    
                except Exception as e:
                    conn.rollback()
                    logger.error(f"[{self.source_name}] Error enriching {cve_id}: {e}")
                    
            status = "success"
            logger.info(f"[{self.source_name}] Successfully enriched {processed} CVEs.")
        except Exception as e:
            logger.error(f"[{self.source_name}] Collector execution failed: {e}")
        finally:
            log_feed_run(len(cves_to_enrich), processed, status)
            cursor.close()
            conn.close()

def main():
    collector = NVDCollector()
    collector.run()

if __name__ == "__main__":
    main()
