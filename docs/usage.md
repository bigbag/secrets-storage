# Usage

`secrets-storage` resolves a name from configured providers. `Secrets` checks
providers in declaration order and skips any whose `enabled` property is false.

```python
from secrets_storage import ENVStorage, Secrets

secrets = Secrets([ENVStorage()])
value = secrets.get("API_TOKEN", fallback_value="local-development-token")
```

## Missing values and fallbacks

Providers return `MISSING` only when a key is absent. `""`, `0`, `False`, and
`None` are values and are returned unchanged. An explicit `fallback_value`,
including `None` or `False`, is returned only after every enabled provider
reports `MISSING`. Without a fallback, `Secrets.get()` raises
`SecretNotFoundError`.

Custom providers subclass `BaseStorage`, implement `enabled`, and return either
a value or `MISSING` from `get_secret(name)`.

## Environment variables

`ENVStorage` reads the process environment. Set `available=False` to leave it
configured but exclude it from lookups:

```python
from secrets_storage import ENVStorage

storage = ENVStorage(available=False)
```

## HashiCorp Vault

`VaultStorage` eagerly authenticates and reads one KV path at construction. It
uses the supported `hvac` 2.x API; `hvac` 3.x is intentionally excluded until
its compatibility is evaluated. It uses Kubernetes authentication with the
service-account token at `/var/run/secrets/kubernetes.io/serviceaccount/token`
by default.

```python
from secrets_storage import VaultStorage

storage = VaultStorage(
    host="https://vault.example",
    namespace="secret/application",
    role="application",
    kv_version="v2",
    auth_mount_point="kubernetes",
)
```

TLS certificate verification is enabled by default. Set `ssl_verify` to a CA
bundle path when Vault uses a private CA; set it to `False` only for controlled
local development.

KV v1 responses are read from `data`; KV v2 responses are read from
`data.data`. Use `available=False` to create a disabled Vault provider without
requiring host, role, token, or network access.

`StorageConfigurationError` identifies invalid local Vault configuration or an
unreadable/empty service-account token. `VaultAuthenticationError` identifies
Kubernetes login failures or missing client tokens. `VaultResponseError`
identifies Vault read failures and malformed KV payloads. These errors include
only safe configuration context and never include a secret value or JWT.

Run `uv run python examples/vault_kubernetes.py` only where `VAULT_ADDR`,
`VAULT_NAMESPACE`, `VAULT_ROLE`, and a Kubernetes service-account token are
available.
