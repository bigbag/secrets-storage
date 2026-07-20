import secrets_storage


def test_public_api_has_expected_version_and_exports() -> None:
    assert secrets_storage.__version__ == "1.0.0"
    assert secrets_storage.__all__ == [
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
