"""Docker Compose secrets management"""

from pathlib import Path
from typing import Optional


class SecretsManager:
    """Manage Docker Compose secrets."""

    SECRETS_DIR = Path("/run/secrets")

    @classmethod
    def get_secret(cls, secret_name: str) -> str:
        """Read a secret from Docker secrets mount."""
        secret_file = cls.SECRETS_DIR / secret_name

        if not secret_file.exists():
            raise FileNotFoundError(
                f"Secret '{secret_name}' not found at {secret_file}. "
                f"Ensure the secret is properly mounted in docker-compose.yml"
            )

        try:
            content = secret_file.read_text().strip()
            if not content:
                raise ValueError(f"Secret '{secret_name}' is empty")
            return content
        except Exception as e:
            raise RuntimeError(f"Error reading secret '{secret_name}': {e}")

    @classmethod
    def get_optional_secret(cls, secret_name: str) -> Optional[str]:
        """Get an optional secret, returns None if not found."""
        try:
            return cls.get_secret(secret_name)
        except (FileNotFoundError, RuntimeError):
            return None

    @classmethod
    def list_available_secrets(cls) -> list[str]:
        """List all available secrets."""
        if not cls.SECRETS_DIR.exists():
            return []
        return [f.name for f in cls.SECRETS_DIR.iterdir() if f.is_file()]