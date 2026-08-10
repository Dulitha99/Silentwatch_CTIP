import feedparser
from typing import List, Dict, Any
from collectors.utils.logger import logger

class RSSParser:
    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        # Set a proper user agent for security feeds
        self.user_agent = "SilentWatch-CTIP/1.0 (+https://github.com/silentwatch)"

    def fetch_feed(self, url: str) -> List[Dict[str, Any]]:
        """
        Fetches and parses an RSS or Atom feed using feedparser.
        Handles timeout and user-agent implicitly via feedparser config.
        Returns a list of entry dictionaries.
        """
        try:
            # Set global timeout for feedparser (it uses urllib internally)
            import socket
            socket.setdefaulttimeout(self.timeout)
            
            parsed_feed = feedparser.parse(url, agent=self.user_agent)
            
            # bozo=1 means feedparser detected an issue (like malformed XML)
            if parsed_feed.bozo and hasattr(parsed_feed, 'bozo_exception'):
                logger.warning(f"Feed at {url} may be malformed (bozo exception): {parsed_feed.bozo_exception}")
                # Sometimes it still parses correctly despite bozo being 1, so we continue

            if not parsed_feed.entries:
                if 'status' in parsed_feed and parsed_feed.status >= 400:
                    logger.error(f"Failed to fetch feed at {url}. HTTP Status: {parsed_feed.status}")
                else:
                    logger.warning(f"No entries found in feed at {url}")
                return []
                
            return parsed_feed.entries
            
        except Exception as e:
            logger.error(f"Exception while parsing feed {url}: {e}")
            return []
