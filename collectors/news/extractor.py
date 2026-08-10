import sys
import os
import psycopg2
from psycopg2.extras import Json

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from collectors.base_collector import BaseCollector
from collectors.utils.logger import logger

from collectors.news.regex_patterns import extract_regex_entities
from collectors.news.entity_matcher import extract_dictionary_entities
from collectors.news.correlation import Correlator

class IntelligenceExtractor(BaseCollector):
    def __init__(self):
        super().__init__(
            source_name="News Extractor & Correlator",
            source_type="Intelligence Engine",
            trust_score=100
        )

    def fetch_data(self):
        pass

    def process_data(self, data):
        pass
        
    def _calculate_confidence(self, entity_type: str, count: int) -> str:
        """
        Determines the confidence level of an extraction.
        Regex match = Medium, Dictionary match = High, Multiple occurrences = Very High
        """
        if count > 1:
            return "Very High"
        if entity_type in ["vendors", "products", "threat_actors", "malware"]:
            return "High"
        return "Medium"

    def run(self):
        logger.info(f"Starting {self.source_name}")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        correlator = Correlator(cursor)
        
        # We only process articles where related_iocs is NULL (meaning they haven't been analyzed yet)
        cursor.execute("SELECT id, title, summary, content FROM cyber_news WHERE related_iocs IS NULL")
        articles = cursor.fetchall()
        
        total_articles = len(articles)
        total_extracted = 0
        total_correlations = 0
        total_failures = 0
        
        for article in articles:
            article_id, title, summary, content = article
            
            print(f"Processing article {article_id}")
            
            # Combine text fields for analysis safely
            full_text = f"{title or ''} {summary or ''} {content or ''}"
            
            try:
                # 1. Extraction
                regex_entities = extract_regex_entities(full_text)
                dict_entities = extract_dictionary_entities(full_text)
                
                # Combine all potential indicators (for correlation lookup)
                all_iocs = []
                all_iocs.extend(regex_entities.get("ipv4", []))
                all_iocs.extend(regex_entities.get("ipv6", []))
                all_iocs.extend(regex_entities.get("domains", []))
                all_iocs.extend(regex_entities.get("urls", []))
                all_iocs.extend(regex_entities.get("emails", []))
                all_iocs.extend(regex_entities.get("md5", []))
                all_iocs.extend(regex_entities.get("sha1", []))
                all_iocs.extend(regex_entities.get("sha256", []))
                
                cves = regex_entities.get("cves", [])
                ips_count = len(regex_entities.get("ipv4", [])) + len(regex_entities.get("ipv6", []))
                domains_count = len(regex_entities.get("domains", [])) + len(regex_entities.get("urls", []))
                actors = dict_entities.get("threat_actors", [])
                malware = dict_entities.get("malware", [])
                vendors = dict_entities.get("vendors", [])
                products = dict_entities.get("products", [])
                
                # Count total entities extracted for metrics
                entities_count = len(cves) + ips_count + domains_count + len(actors) + len(malware) + len(vendors) + len(products)
                total_extracted += entities_count
                
                print(f"\nCVEs:\n{len(cves)}")
                print(f"\nIPs:\n{ips_count}")
                print(f"\nDomains:\n{domains_count}")
                print(f"\nThreat Actors:\n{len(actors)}")
                print(f"\nMalware:\n{len(malware)}")
                
                # 2. Correlation
                correlated_cves = correlator.correlate_cves(cves)
                correlated_iocs = correlator.correlate_indicators(all_iocs)
                
                print(f"\nRelated vulnerabilities:\n{len(correlated_cves)}")
                print(f"\nRelated indicators:\n{len(correlated_iocs)}\n")
                
                total_correlations += len(correlated_cves) + len(correlated_iocs)
                
                # 3. Update database JSONB fields
                cursor.execute("""
                    UPDATE cyber_news 
                    SET related_cves = %s,
                        related_iocs = %s,
                        related_vendors = %s,
                        related_products = %s,
                        related_threat_actors = %s,
                        related_malware = %s
                    WHERE id = %s
                """, (
                    Json(correlated_cves),
                    Json(correlated_iocs),
                    Json(vendors),
                    Json(products),
                    Json(actors),
                    Json(malware),
                    article_id
                ))
                
                conn.commit()
                print("Updated article\n")
                
                # Logging to app logs
                logger.debug(f"Article {article_id} processed: {entities_count} entities, {len(correlated_cves) + len(correlated_iocs)} correlations")
                
            except Exception as e:
                conn.rollback()
                logger.error(f"Error processing article {article_id}: {e}")
                total_failures += 1
                print(f"Failed article {article_id}\n")

        cursor.close()
        conn.close()
        
        print("Completed\n")
        print(f"Articles processed:\n{total_articles}")
        print(f"Entities extracted:\n{total_extracted}")
        print(f"Correlations:\n{total_correlations}")
        print(f"Failures:\n{total_failures}")
        
        logger.info("Extraction Completed")
        logger.info(f"Articles processed: {total_articles}")
        logger.info(f"Entities extracted: {total_extracted}")
        logger.info(f"Correlations: {total_correlations}")
        logger.info(f"Failures: {total_failures}")

def main():
    extractor = IntelligenceExtractor()
    extractor.run()

if __name__ == "__main__":
    main()
