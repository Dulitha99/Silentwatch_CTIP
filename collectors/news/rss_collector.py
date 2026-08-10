import sys
import os
import psycopg2
from psycopg2.extras import Json

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from collectors.base_collector import BaseCollector
from collectors.utils.logger import logger
from collectors.utils.feed_logger import log_feed_run

from collectors.news.loader import NewsSourceLoader
from collectors.news.parser import RSSParser
from collectors.news.normalizer import ArticleNormalizer

class RSSCollector(BaseCollector):
    def __init__(self):
        super().__init__(
            source_name="Generic RSS/Atom News Collector",
            source_type="News Intelligence",
            trust_score=90
        )
        self.loader = NewsSourceLoader.get_instance()
        self.parser = RSSParser()

    def fetch_data(self):
        # We override run() because we have multiple sources to iterate through
        pass

    def process_data(self, data):
        pass

    def run(self):
        logger.info(f"Starting {self.source_name} collector")
        
        # Load all enabled sources
        sources = self.loader.get_enabled_sources()
        logger.info(f"Loading registry")
        print(f"Loaded {len(sources)} sources\n")
        
        total_sources = len(sources)
        total_articles_received = 0
        total_articles_inserted = 0
        total_duplicates = 0
        total_failures = 0
        
        conn = self.get_connection()
        
        for source in sources:
            print(f"Collecting:\n{source.name}\n")
            logger.info(f"Collecting source: {source.name} ({source.rss_url})")
            
            # Fetch feed using the parser
            entries = self.parser.fetch_feed(source.rss_url)
            
            if not entries:
                total_failures += 1
                logger.error(f"Failures collecting from {source.name}")
                continue
                
            total_articles_received += len(entries)
            
            inserted = 0
            duplicates = 0
            
            cursor = conn.cursor()
            # Ensure the source ID exists in intelligence_sources to maintain FK integrity
            # We override source_name temporarily so get_source_id works for each specific news source
            original_source_name = self.source_name
            original_trust_score = self.trust_score
            self.source_name = source.name
            self.trust_score = source.trust_score
            source_id = self.get_source_id(cursor)
            self.source_name = original_source_name
            self.trust_score = original_trust_score
            
            for entry in entries:
                # Normalize article structure
                normalized = ArticleNormalizer.normalize(entry, source)
                
                try:
                    # Database Insert with ON CONFLICT DO NOTHING
                    # Duplicate detection works by hashing the source name and URL
                    # This ensures we don't insert the same article twice even if it reappears in the RSS feed
                    cursor.execute("""
                        INSERT INTO cyber_news (
                            title, summary, content, url, source, category, author, 
                            published_date, language, article_hash, tags
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        ) ON CONFLICT (article_hash) DO NOTHING
                        """, (
                            normalized['title'],
                            normalized['summary'],
                            normalized['content'],
                            normalized['url'],
                            normalized['source'],
                            normalized['category'],
                            normalized['author'],
                            normalized['published_date'],
                            normalized['language'],
                            normalized['article_hash'],
                            Json(normalized['tags'])
                        ))
                    
                    if cursor.rowcount > 0:
                        inserted += 1
                    else:
                        duplicates += 1
                        
                except Exception as e:
                    conn.rollback()
                    logger.error(f"Error inserting article {normalized['url']}: {e}")
                    
            conn.commit()
            cursor.close()
            
            total_articles_inserted += inserted
            total_duplicates += duplicates
            
            print(f"Inserted {inserted} articles\n")
            logger.info(f"Number of articles: {len(entries)}")
            logger.info(f"Inserted: {inserted}")
            logger.info(f"Skipped duplicates: {duplicates}")
            
            # Update feed_history for this specific source run
            # Temporarily trick log_feed_run since it uses the global logger which is fine,
            # but feed_logger uses the class instance if it was a class method, but log_feed_run is standalone
            log_feed_run(len(entries), inserted, "success")
            
        conn.close()
        
        print("Completed\n")
        print(f"Sources processed: {total_sources}")
        print(f"Articles received: {total_articles_received}")
        print(f"Inserted: {total_articles_inserted}")
        print(f"Duplicates: {total_duplicates}")
        print(f"Failures: {total_failures}")
        
        logger.info("Completion summary:")
        logger.info(f"Sources processed: {total_sources}")
        logger.info(f"Articles received: {total_articles_received}")
        logger.info(f"Inserted: {total_articles_inserted}")
        logger.info(f"Duplicates: {total_duplicates}")
        logger.info(f"Failures: {total_failures}")

def main():
    collector = RSSCollector()
    collector.run()

if __name__ == "__main__":
    main()
