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


def get_user_roles(username: str) -> list[str]:
    """Mock database call to get user roles.

    In production, this would query a database to retrieve
    the roles associated with a user.

    Args:
        username: The username to look up

    Returns:
        List of roles for the user (defaults to ["user"])
    """
    # Mock implementation - in production, query your database
    # Example: return db.query(User).filter(User.username == username).first().roles
    return ["user"]
