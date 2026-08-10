import hashlib
from datetime import datetime
from time import mktime
from typing import Dict, Any

from collectors.news.sources import NewsSource

class ArticleNormalizer:
    @staticmethod
    def _generate_article_hash(source_name: str, url: str) -> str:
        """
        Duplicate detection works by hashing the source name and article URL.
        This generates a unique SHA256 string used for PostgreSQL ON CONFLICT DO NOTHING.
        """
        hash_input = f"{source_name}{url}".encode('utf-8')
        return hashlib.sha256(hash_input).hexdigest()

    @staticmethod
    def _parse_published_date(entry: Dict[str, Any]) -> datetime:
        """Extracts and standardizes the published date from feedparser entry."""
        if 'published_parsed' in entry and entry.published_parsed:
            return datetime.fromtimestamp(mktime(entry.published_parsed))
        elif 'updated_parsed' in entry and entry.updated_parsed:
            return datetime.fromtimestamp(mktime(entry.updated_parsed))
        else:
            return datetime.utcnow()

    @staticmethod
    def normalize(entry: Dict[str, Any], source: NewsSource) -> Dict[str, Any]:
        """
        Normalizes a raw feedparser entry into the standard cyber_news schema.
        Extracts title, url, content, and computes the article_hash.
        """
        url = entry.get('link', '')
        title = entry.get('title', 'Unknown Title')
        
        # Summary and Content extraction
        summary = entry.get('summary', '')
        content = ''
        if 'content' in entry and len(entry.content) > 0:
            content = entry.content[0].get('value', '')
        
        # Fallback to summary if content is unavailable
        if not content:
            content = summary

        author = entry.get('author', 'Unknown')
        published_date = ArticleNormalizer._parse_published_date(entry)
        
        # Tags combining source tags and entry tags
        tags = list(source.tags)
        if 'tags' in entry:
            entry_tags = [t.get('term') for t in entry.tags if t.get('term')]
            tags.extend(entry_tags)
            tags = list(set(tags)) # Deduplicate

        article_hash = ArticleNormalizer._generate_article_hash(source.name, url)

        return {
            "title": title,
            "summary": summary,
            "content": content,
            "url": url,
            "source": source.name,
            "category": source.category,
            "author": author,
            "published_date": published_date,
            "language": "en", # Defaulting to english for now
            "article_hash": article_hash,
            "tags": tags
        }
