import os
import json
from typing import List

from collectors.utils.logger import logger
from collectors.news.sources import NewsSource

# Default path assuming script is run from project root or inside collectors
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "config", "news_sources.json")

class NewsSourceLoader:
    def __init__(self, config_path: str = CONFIG_PATH):
        self.config_path = config_path
        self._sources: List[NewsSource] = []
        self.load_sources()

    def load_sources(self):
        """Loads and validates sources from the JSON configuration."""
        if not os.path.exists(self.config_path):
            logger.error(f"News sources configuration file not found: {self.config_path}")
            return
            
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if not isinstance(data, list):
                logger.error("Invalid format in news_sources.json. Expected a list of sources.")
                return

            self._sources = []
            for item in data:
                try:
                    # Validate required fields
                    required_fields = ["id", "name", "category", "type", "rss_url", "website", "trust_score", "enabled", "collection_interval"]
                    for field in required_fields:
                        if field not in item:
                            raise ValueError(f"Missing required field: {field}")
                            
                    source = NewsSource(
                        id=item["id"],
                        name=item["name"],
                        category=item["category"],
                        type=item["type"],
                        rss_url=item["rss_url"],
                        website=item["website"],
                        trust_score=item["trust_score"],
                        enabled=item["enabled"],
                        collection_interval=item["collection_interval"],
                        tags=item.get("tags", [])
                    )
                    self._sources.append(source)
                except Exception as e:
                    logger.error(f"Failed to load source {item.get('id', 'Unknown')}: {e}")
                    
            logger.info(f"Successfully loaded {len(self._sources)} news sources.")
            
        except json.JSONDecodeError as e:
            logger.error(f"Malformed JSON in news_sources.json: {e}")
        except Exception as e:
            logger.error(f"Unexpected error loading news sources: {e}")

    def get_all_sources(self) -> List[NewsSource]:
        return self._sources
        
    def get_enabled_sources(self) -> List[NewsSource]:
        return [s for s in self._sources if s.enabled]
        
    def get_sources_by_category(self, category: str) -> List[NewsSource]:
        return [s for s in self._sources if s.enabled and s.category.lower() == category.lower()]
        
    def get_sources_by_type(self, source_type: str) -> List[NewsSource]:
        return [s for s in self._sources if s.enabled and s.type.lower() == source_type.lower()]

    @classmethod
    def get_instance(cls):
        """Returns a loaded instance of NewsSourceLoader"""
        return cls()
