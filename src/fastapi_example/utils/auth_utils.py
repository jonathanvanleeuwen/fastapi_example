"""Authentication utility functions."""

import hashlib


def hash_api_key(api_key: str) -> str:
    """Hash an API key using SHA256.

    Args:
        api_key: The plain text API key to hash

    Returns:
        The hashed API key as a hexadecimal string
    """
    return hashlib.sha256(api_key.encode()).hexdigest()
