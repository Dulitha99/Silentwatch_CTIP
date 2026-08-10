from dataclasses import dataclass, field
from typing import List

@dataclass
class NewsSource:
    id: str
    name: str
    category: str
    type: str
    rss_url: str
    website: str
    trust_score: int
    enabled: bool
    collection_interval: int
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "type": self.type,
            "rss_url": self.rss_url,
            "website": self.website,
            "trust_score": self.trust_score,
            "enabled": self.enabled,
            "collection_interval": self.collection_interval,
            "tags": self.tags
        }
