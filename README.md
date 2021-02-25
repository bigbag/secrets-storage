# secrets-storage

[![CI](https://github.com/bigbag/secrets-storage/workflows/CI/badge.svg)](https://github.com/bigbag/secrets-storage/actions?query=workflow%3ACI)
[![codecov](https://codecov.io/gh/bigbag/secrets-storage/branch/main/graph/badge.svg?token=FQTY888XG1)](https://codecov.io/gh/bigbag/secrets-storage)
[![pypi](https://img.shields.io/pypi/v/secrets-storage.svg)](https://pypi.python.org/pypi/secrets-storage)
[![downloads](https://img.shields.io/pypi/dm/secrets-storage.svg)](https://pypistats.org/packages/secrets-storage)
[![versions](https://img.shields.io/pypi/pyversions/secrets-storage.svg)](https://github.com/bigbag/secrets-storage)
[![license](https://img.shields.io/github/license/bigbag/secrets-storage.svg)](https://github.com/bigbag/secrets-storage/blob/master/LICENSE)


**secrets-storage** is a helper for getting secrets from different storage.


## Installation

secrets-storage is available on PyPI.
Use pip to install:

    $ pip install secrets-storage

## Basic Usage

```py
from secrets_storage import VaultStorage, ENVStorage, Secrets

IS_PROD = True

vault_storage = VaultStorage(
    host="VAULT_ADDR",
    namespace="VAULT_PATH",
    role="VAULT_ROLE",
    available=IS_PROD,
)

secrets = Secrets(storages=[vault_storage, ENVStorage()])


secrets.get("TEST_PASSWOD")
```

## License

secrets-storage is developed and distributed under the Apache 2.0 license.

## Reporting a Security Vulnerability

See our [security policy](https://github.com/bigbag/secrets-storage/security/policy).
