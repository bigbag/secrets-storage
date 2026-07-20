# secrets-storage

Typed secret lookup from environment variables and HashiCorp Vault.

## Requirements

- Python 3.11+
- `hvac` 2.x only when using `VaultStorage` (installed automatically)

## Install

```console
uv add secrets-storage
```

```console
pip install secrets-storage
```

## Quick start

```python
from secrets_storage import ENVStorage, Secrets

secrets = Secrets([ENVStorage()])
api_token = secrets.get("API_TOKEN", fallback_value="development-token")
```

Providers are checked in declaration order. Disabled providers are skipped.
`""`, `0`, `False`, and `None` are valid stored values; only the exported
`MISSING` sentinel represents an absent secret.

Use `VaultStorage` before `ENVStorage` when Vault should take precedence:

```python
from secrets_storage import ENVStorage, Secrets, VaultStorage

secrets = Secrets([VaultStorage(host="https://vault.example", namespace="secret/app", role="app"), ENVStorage()])
```

See the [usage guide](docs/usage.md), [development guide](docs/development.md),
and [changelog](CHANGELOG.md).

## License

secrets-storage is distributed under the Apache License 2.0.

## Security

Report vulnerabilities through the [security policy](https://github.com/bigbag/secrets-storage/security/policy).
