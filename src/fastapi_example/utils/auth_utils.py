import hashlib


def hash_api_key(api_key: str) -> str:
    """Hash an API key using SHA256.

    Args:
        api_key: The plain text API key to hash

    Returns:
        The hashed API key as a hexadecimal string
    """
    return hashlib.sha256(api_key.encode()).hexdigest()


def get_user_roles(user_email: str) -> list[str]:
    """Get roles for a user based on their email.

    This is a simple implementation that assigns roles based on email domain
    or other criteria. In production, this should query a database or
    external service.

    Args:
        user_email: The user's email address

    Returns:
        List of roles assigned to the user
    """
    # Default role for all authenticated users
    roles = ["user"]

    # Add admin role for specific criteria (customize as needed)
    # Example: admins are users from certain domains or specific emails
    admin_domains = ["admin.com", "company.com"]
    admin_emails = ["admin@example.com"]

    if user_email in admin_emails or any(
        user_email.endswith(f"@{domain}") for domain in admin_domains
    ):
        roles.append("admin")

    return roles
