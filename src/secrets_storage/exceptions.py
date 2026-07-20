"""Exception hierarchy for secrets-storage."""


class SecretsStorageError(Exception):
    """Base exception for secrets-storage failures."""


class SecretNotFoundError(SecretsStorageError):
    """Raised when no enabled storage contains a requested secret."""


class StorageConfigurationError(SecretsStorageError):
    """Raised when a storage has invalid local configuration."""


class VaultAuthenticationError(SecretsStorageError):
    """Raised when Vault Kubernetes authentication cannot yield a client token."""


class VaultResponseError(SecretsStorageError):
    """Raised when Vault returns a response that is not a supported KV payload."""
