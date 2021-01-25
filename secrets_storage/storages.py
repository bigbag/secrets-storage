import abc
import os
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

import hvac


class BaseStorage(abc.ABC):
    name: str
    available: bool

    @property
    @abc.abstractmethod
    def enabled(self) -> bool:
        pass

    @abc.abstractmethod
    def get_secret(self, name: str, fallback_value: Optional[Any] = None) -> Any:
        pass


@dataclass
class VaultStorage(BaseStorage):
    host: str
    namespace: str
    role: str

    name: str = "vault_storage"
    available: bool = False
    ssl_verify: bool = False

    kube_token_path: str = "/var/run/secrets/kubernetes.io/serviceaccount/token"

    secrets: Dict[str, Any] = field(init=False, repr=False)

    def __post_init__(self):
        if not self.enabled:
            self.secrets = {}
        else:
            self.secrets = self._get_secrets()

    def _get_secrets(self):
        with open(self.kube_token_path) as f:
            client = hvac.Client(url=self.host, verify=self.ssl_verify)
            auth_info = client.auth_kubernetes(role=self.role, jwt=f.read())
            token = auth_info.get("auth", {}).get("client_token")
            if not token:
                raise ValueError("Not found vault token.")

            client.token = token
            return client.read(self.namespace).get("data", {})

    @property
    def enabled(self) -> bool:
        return bool(self.available and self.host and self.kube_token_path and self.namespace)

    def get_secret(self, name: str, fallback_value: Optional[Any] = None) -> Any:
        return self.secrets.get(name)


@dataclass
class ENVStorage(BaseStorage):
    name: str = "env_storage"
    available: bool = True

    @property
    def enabled(self) -> bool:
        return bool(self.available)

    def get_secret(self, name: str, fallback_value: Optional[Any] = None) -> Any:
        return os.getenv(name, fallback_value)
