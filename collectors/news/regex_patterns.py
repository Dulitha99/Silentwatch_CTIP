import re

# Centralized Regex Patterns for IOC extraction

# CVEs: Matches CVE-YYYY-NNNNNN
CVE_PATTERN = re.compile(r'\bCVE-\d{4}-\d{4,7}\b', re.IGNORECASE)

# IPv4: Matches standard IPv4 addresses (doesn't filter private yet)
IPV4_PATTERN = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')

# IPv6: Standard IPv6 (simplified for typical IOCs)
IPV6_PATTERN = re.compile(r'\b(?:[A-Fa-f0-9]{1,4}:){7}[A-Fa-f0-9]{1,4}\b|\b(?:[A-Fa-f0-9]{1,4}:)*::(?:[A-Fa-f0-9]{1,4}:)*[A-Fa-f0-9]{1,4}\b')

# MD5, SHA1, SHA256 hashes
MD5_PATTERN = re.compile(r'\b[a-fA-F0-9]{32}\b')
SHA1_PATTERN = re.compile(r'\b[a-fA-F0-9]{40}\b')
SHA256_PATTERN = re.compile(r'\b[a-fA-F0-9]{64}\b')

# MITRE ATT&CK IDs (e.g., T1059, T1059.001)
MITRE_PATTERN = re.compile(r'\bT\d{4}(?:\.\d{3})?\b')

# Email Addresses
EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')

# Domains (simplified, extracts typical domains)
DOMAIN_PATTERN = re.compile(r'\b(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]\b', re.IGNORECASE)

# URLs (http/https/ftp)
URL_PATTERN = re.compile(r'\b(?:http|https|ftp)://[^\s/$.?#].[^\s]*\b', re.IGNORECASE)

def extract_regex_entities(text: str) -> dict:
    """
    Extracts all regex-based IOCs from a given text.
    Returns a dictionary of deduplicated lists.
    """
    if not text:
        return {}

    return {
        "cves": list(set([c.upper() for c in CVE_PATTERN.findall(text)])),
        "ipv4": list(set(IPV4_PATTERN.findall(text))),
        "ipv6": list(set(IPV6_PATTERN.findall(text))),
        "md5": list(set([h.lower() for h in MD5_PATTERN.findall(text)])),
        "sha1": list(set([h.lower() for h in SHA1_PATTERN.findall(text)])),
        "sha256": list(set([h.lower() for h in SHA256_PATTERN.findall(text)])),
        "mitre": list(set([m.upper() for m in MITRE_PATTERN.findall(text)])),
        "emails": list(set([e.lower() for e in EMAIL_PATTERN.findall(text)])),
        # Basic domain filtering to avoid extracting standard sentences ending in periods as domains
        "domains": list(set([d.lower() for d in DOMAIN_PATTERN.findall(text) if '.' in d and len(d) > 3])),
        "urls": list(set(URL_PATTERN.findall(text)))
    }
