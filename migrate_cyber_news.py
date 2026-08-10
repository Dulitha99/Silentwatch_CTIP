import sys
import os
sys.path.append(r"D:\Repos\Silentwatch_CTIP")
from dotenv import load_dotenv
load_dotenv()
from collectors.utils.database import get_connection

def migrate_cyber_news():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # 1. Drop existing table if it exists
        cursor.execute("DROP TABLE IF EXISTS cyber_news;")
        
        # 2. Recreate with the new schema
        cursor.execute("""
        CREATE TABLE cyber_news (
            id SERIAL PRIMARY KEY,
            title TEXT,
            summary TEXT,
            content TEXT,
            url TEXT UNIQUE,
            source VARCHAR(100),
            category VARCHAR(100),
            author VARCHAR(100),
            published_date TIMESTAMP,
            language VARCHAR(20),
            article_hash VARCHAR(64) UNIQUE,
            related_cves JSONB,
            related_iocs JSONB,
            related_vendors JSONB,
            related_products JSONB,
            related_threat_actors JSONB,
            related_malware JSONB,
            tags JSONB,
            severity VARCHAR(20),
            sentiment VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # 3. Create indexes
        cursor.execute("CREATE INDEX idx_cyber_news_article_hash ON cyber_news(article_hash);")
        cursor.execute("CREATE INDEX idx_cyber_news_published_date ON cyber_news(published_date);")
        cursor.execute("CREATE INDEX idx_cyber_news_source ON cyber_news(source);")
        cursor.execute("CREATE INDEX idx_cyber_news_severity ON cyber_news(severity);")
        
        conn.commit()
        print("Successfully migrated cyber_news schema!")
        
    except Exception as e:
        conn.rollback()
        print(f"Error during migration: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    migrate_cyber_news()
