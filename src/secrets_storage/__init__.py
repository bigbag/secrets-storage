"""Typed secret lookup from environment variables and HashiCorp Vault."""

from .exceptions import (
    SecretNotFoundError,
    SecretsStorageError,
    StorageConfigurationError,
    VaultAuthenticationError,
    VaultResponseError,
)
from .secrets import Secrets
from .storages import MISSING, BaseStorage, ENVStorage, VaultStorage

__version__ = "1.0.0"

__all__ = [
    "BaseStorage",
    "ENVStorage",
    "MISSING",
    "SecretNotFoundError",
    "Secrets",
    "SecretsStorageError",
    "StorageConfigurationError",
    "VaultAuthenticationError",
    "VaultResponseError",
    "VaultStorage",
    "__version__",
]
