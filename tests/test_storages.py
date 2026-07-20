import pytest

from secrets_storage import (
    MISSING,
    ENVStorage,
    StorageConfigurationError,
    VaultAuthenticationError,
    VaultResponseError,
    VaultStorage,
)


def test_environment_storage_returns_value(monkeypatch) -> None:
    monkeypatch.setenv("API_TOKEN", "token")
    assert ENVStorage().get_secret("API_TOKEN") == "token"


def test_environment_storage_marks_an_unset_name_as_missing(monkeypatch) -> None:
    monkeypatch.delenv("API_TOKEN", raising=False)
    assert ENVStorage().get_secret("API_TOKEN") is MISSING


def test_environment_storage_can_be_disabled() -> None:
    assert ENVStorage(available=False).enabled is False


def test_vault_rejects_unknown_kv_version() -> None:
    with pytest.raises(StorageConfigurationError, match="kv_version"):
        VaultStorage(host="http://vault", namespace="secret/app", role="app", kv_version="v3")


def test_vault_rejects_empty_required_configuration() -> None:
    with pytest.raises(StorageConfigurationError, match="host"):
        VaultStorage(host="", namespace="secret/app", role="app")


def test_vault_rejects_missing_service_account_token(tmp_path) -> None:
    with pytest.raises(StorageConfigurationError, match="token"):
        VaultStorage(
            host="http://vault",
            namespace="secret/app",
            role="app",
            auth_token_path=str(tmp_path / "missing"),
        )


def test_vault_rejects_an_empty_service_account_token(tmp_path) -> None:
    token = tmp_path / "token"
    token.write_text("", encoding="utf-8")
    with pytest.raises(StorageConfigurationError, match="must not be empty"):
        VaultStorage(
            host="http://vault", namespace="secret/app", role="app", auth_token_path=str(token)
        )


def test_vault_rejects_a_payload_without_kv_data(tmp_path, requests_mock) -> None:
    token = tmp_path / "token"
    token.write_text("jwt", encoding="utf-8")
    requests_mock.post(
        "http://vault/v1/auth/kubernetes/login", json={"auth": {"client_token": "token"}}
    )
    requests_mock.get("http://vault/v1/secret/app", json={})
    with pytest.raises(VaultResponseError, match="secret/app"):
        VaultStorage(
            host="http://vault", namespace="secret/app", role="app", auth_token_path=str(token)
        )


def test_vault_rejects_a_non_mapping_response(tmp_path, requests_mock) -> None:
    token = tmp_path / "token"
    token.write_text("jwt", encoding="utf-8")
    requests_mock.post(
        "http://vault/v1/auth/kubernetes/login", json={"auth": {"client_token": "token"}}
    )
    requests_mock.get("http://vault/v1/secret/app", json=[])
    with pytest.raises(VaultResponseError, match="secret/app"):
        VaultStorage(
            host="http://vault", namespace="secret/app", role="app", auth_token_path=str(token)
        )


def test_vault_rejects_malformed_kv2_payload(tmp_path, requests_mock) -> None:
    token = tmp_path / "token"
    token.write_text("jwt", encoding="utf-8")
    requests_mock.post(
        "http://vault/v1/auth/kubernetes/login", json={"auth": {"client_token": "token"}}
    )
    requests_mock.get("http://vault/v1/secret/app", json={"data": {"unexpected": "value"}})
    with pytest.raises(VaultResponseError, match="secret/app"):
        VaultStorage(
            host="http://vault",
            namespace="secret/app",
            role="app",
            kv_version="v2",
            auth_token_path=str(token),
        )


@pytest.mark.parametrize(
    ("kv_version", "payload"),
    [
        ("v1", {"data": {"API_TOKEN": "v1-token"}}),
        ("v2", {"data": {"data": {"API_TOKEN": "v2-token"}}}),
    ],
)
def test_vault_reads_supported_kv_payloads(tmp_path, requests_mock, kv_version, payload) -> None:
    token = tmp_path / "token"
    token.write_text("jwt", encoding="utf-8")
    requests_mock.post(
        "http://vault/v1/auth/kubernetes/login", json={"auth": {"client_token": "token"}}
    )
    requests_mock.get("http://vault/v1/secret/app", json=payload)
    vault = VaultStorage(
        host="http://vault",
        namespace="secret/app",
        role="app",
        auth_token_path=str(token),
        kv_version=kv_version,
    )
    assert vault.get_secret("API_TOKEN") == f"{kv_version}-token"
    assert vault.get_secret("MISSING_TOKEN") is MISSING


def test_vault_wraps_kubernetes_authentication_errors(tmp_path, requests_mock) -> None:
    token = tmp_path / "token"
    token.write_text("jwt", encoding="utf-8")
    requests_mock.post("http://vault/v1/auth/kubernetes/login", status_code=500)
    with pytest.raises(VaultAuthenticationError, match="authentication failed"):
        VaultStorage(
            host="http://vault", namespace="secret/app", role="app", auth_token_path=str(token)
        )


def test_vault_rejects_an_auth_response_without_a_client_token(tmp_path, requests_mock) -> None:
    token = tmp_path / "token"
    token.write_text("jwt", encoding="utf-8")
    requests_mock.post("http://vault/v1/auth/kubernetes/login", json={"auth": {}})
    with pytest.raises(VaultAuthenticationError, match="client token"):
        VaultStorage(
            host="http://vault", namespace="secret/app", role="app", auth_token_path=str(token)
        )


def test_vault_wraps_read_errors(tmp_path, requests_mock) -> None:
    token = tmp_path / "token"
    token.write_text("jwt", encoding="utf-8")
    requests_mock.post(
        "http://vault/v1/auth/kubernetes/login", json={"auth": {"client_token": "token"}}
    )
    requests_mock.get("http://vault/v1/secret/app", status_code=500)
    with pytest.raises(VaultResponseError, match="read failed"):
        VaultStorage(
            host="http://vault", namespace="secret/app", role="app", auth_token_path=str(token)
        )


def test_disabled_vault_does_not_require_configuration() -> None:
    vault = VaultStorage(host="", namespace="", role="", available=False)
    assert vault.enabled is False
    assert vault.get_secret("API_TOKEN") is MISSING
