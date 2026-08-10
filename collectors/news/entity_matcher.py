import re

# Dictionaries of known cybersecurity entities

VENDORS = [
    "Microsoft", "Cisco", "Fortinet", "Palo Alto", "CrowdStrike", 
    "SentinelOne", "Google", "VMware", "Sophos", "Ivanti", 
    "Juniper", "Check Point", "Oracle", "Linux", "Apple"
]

PRODUCTS = [
    "Exchange", "SharePoint", "Windows", "Entra ID", "FortiGate", 
    "ESXi", "Chrome", "Edge", "Apache", "Tomcat", "Nginx"
]

THREAT_ACTORS = [
    "APT28", "APT29", "APT41", "Lazarus", "Volt Typhoon", 
    "Sandworm", "Scattered Spider", "FIN7", "Mustang Panda", "UNC2452"
]

MALWARE = [
    "Emotet", "QakBot", "Lumma", "Black Basta", "LockBit", 
    "TrickBot", "RedLine", "AsyncRAT", "StealC", "DarkGate", 
    "Remcos", "AgentTesla", "NanoCore"
]

def build_regex(entities):
    """
    Compiles exact word boundary regexes for highly accurate matching.
    Sorts by length descending to match longest phrases first (e.g., 'Palo Alto' before 'Palo').
    """
    sorted_entities = sorted(entities, key=len, reverse=True)
    pattern = r'\b(?:' + '|'.join(re.escape(e) for e in sorted_entities) + r')\b'
    return re.compile(pattern, re.IGNORECASE)

VENDOR_PATTERN = build_regex(VENDORS)
PRODUCT_PATTERN = build_regex(PRODUCTS)
THREAT_ACTOR_PATTERN = build_regex(THREAT_ACTORS)
MALWARE_PATTERN = build_regex(MALWARE)

def extract_dictionary_entities(text: str) -> dict:
    """
    Extracts entities using compiled dictionary regexes.
    Returns deduplicated and canonical (properly cased) terms based on the original dictionaries.
    """
    if not text:
        return {}

    # Helper to map the lowercase matched text back to the canonical capitalized version
    def map_to_canonical(matches, canonical_list):
        lower_map = {c.lower(): c for c in canonical_list}
        return list(set(lower_map.get(m.lower(), m) for m in matches))

    vendors_found = VENDOR_PATTERN.findall(text)
    products_found = PRODUCT_PATTERN.findall(text)
    actors_found = THREAT_ACTOR_PATTERN.findall(text)
    malware_found = MALWARE_PATTERN.findall(text)

    return {
        "vendors": map_to_canonical(vendors_found, VENDORS),
        "products": map_to_canonical(products_found, PRODUCTS),
        "threat_actors": map_to_canonical(actors_found, THREAT_ACTORS),
        "malware": map_to_canonical(malware_found, MALWARE)
    }
