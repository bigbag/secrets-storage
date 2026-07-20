"""Storage implementations and their shared contract."""

import os
from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

import hvac
from hvac.api.auth_methods import Kubernetes
from hvac.exceptions import VaultError

from .exceptions import StorageConfigurationError, VaultAuthenticationError, VaultResponseError


class _Missing:
    """Sentinel type representing an absent secret."""


MISSING: Final = _Missing()
KV_VERSION1 = "v1"
KV_VERSION2 = "v2"
_SUPPORTED_KV_VERSIONS = frozenset((KV_VERSION1, KV_VERSION2))


class BaseStorage(ABC):
    """Contract implemented by a secret provider."""

    name: str

    @property
    @abstractmethod
    def enabled(self) -> bool:
        """Return whether this provider participates in lookups."""

    @abstractmethod
    def get_secret(self, name: str) -> Any:
        """Return a value or the :data:`MISSING` sentinel."""


@dataclass(frozen=True, slots=True)
class ENVStorage(BaseStorage):
    """Read secrets from process environment variables."""

    name: str = "env_storage"
    available: bool = True

    @property
    def enabled(self) -> bool:
        return self.available

    def get_secret(self, name: str) -> Any:
        return os.environ.get(name, MISSING)


@dataclass(slots=True)
class VaultStorage(BaseStorage):
    """Read a Kubernetes-authenticated HashiCorp Vault KV path eagerly."""

    host: str
    namespace: str
    role: str
    kv_version: str = KV_VERSION1
    name: str = "vault_storage"
    available: bool = True
    ssl_verify: bool | str = True
    auth_mount_point: str = "kubernetes"
    auth_token_path: str = "/var/run/secrets/kubernetes.io/serviceaccount/token"
    secrets: dict[str, Any] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if not self.available:
            self.secrets = {}
            return

        for field_name in ("host", "namespace", "role", "auth_mount_point", "auth_token_path"):
            if not getattr(self, field_name):
                raise StorageConfigurationError(f"Vault {field_name} must not be empty.")
        if self.kv_version not in _SUPPORTED_KV_VERSIONS:
            raise StorageConfigurationError(f"Unsupported Vault kv_version {self.kv_version!r}.")

        self.secrets = self._get_secrets()

    @property
    def enabled(self) -> bool:
        return self.available

    def _get_client_token(self, client: hvac.Client) -> str:
        try:
            service_account_token = Path(self.auth_token_path).read_text(encoding="utf-8").strip()
        except OSError as exc:
            raise StorageConfigurationError("Vault service-account token cannot be read.") from exc
        if not service_account_token:
            raise StorageConfigurationError("Vault service-account token must not be empty.")

        try:
            response: object = Kubernetes(client.adapter).login(
                role=self.role,
                jwt=service_account_token,
                mount_point=self.auth_mount_point,
            )
        except KeyError as exc:
            raise VaultAuthenticationError(
                "Vault authentication response did not contain a client token."
            ) from exc
        except VaultError as exc:
            raise VaultAuthenticationError("Vault Kubernetes authentication failed.") from exc

        if not isinstance(response, Mapping):
            raise VaultAuthenticationError(
                "Vault authentication response did not contain a client token."
            )
        auth = response.get("auth")
        token = auth.get("client_token") if isinstance(auth, Mapping) else None
        if not isinstance(token, str) or not token:
            raise VaultAuthenticationError(
                "Vault authentication response did not contain a client token."
            )
        return token

    def _parse_secrets(self, response: Mapping[str, Any]) -> dict[str, Any]:
        data = response.get("data")
        if self.kv_version == KV_VERSION2:
            data = data.get("data") if isinstance(data, Mapping) else None
        if not isinstance(data, Mapping):
            raise VaultResponseError(
                f"Vault response for {self.namespace!r} is not a valid KV payload."
            )
        return dict(data)

    def _get_secrets(self) -> dict[str, Any]:
        client = hvac.Client(url=self.host, verify=self.ssl_verify)
        client.token = self._get_client_token(client)
        try:
            response: object = client.read(self.namespace)
        except VaultError as exc:
            raise VaultResponseError(f"Vault read failed for {self.namespace!r}.") from exc
        if not isinstance(response, Mapping):
            raise VaultResponseError(
                f"Vault response for {self.namespace!r} is not a valid KV payload."
            )
        return self._parse_secrets(response)

    def get_secret(self, name: str) -> Any:
        return self.secrets.get(name, MISSING)
