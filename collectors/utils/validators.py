import re

def is_valid_ip(ip: str) -> bool:
    pattern = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
    return bool(pattern.match(ip))

def is_valid_md5(hash_str: str) -> bool:
    return bool(re.match(r"^[a-fA-F0-9]{32}$", hash_str))

def is_valid_sha256(hash_str: str) -> bool:
    return bool(re.match(r"^[a-fA-F0-9]{64}$", hash_str))
