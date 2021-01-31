secrets-storage
=======================================================================

.. image:: https://github.com/bigbag/secrets-storage/workflows/CI/badge.svg
   :target: https://github.com/bigbag/secrets-storage/actions?query=workflow%3ACI
.. image:: https://img.shields.io/pypi/v/secrets-storage.svg
   :target: https://pypi.python.org/pypi/secrets-storage


**secrets-storage** is a helper for getting secrets from different storage.


Installation
------------
secrets-storage is available on PyPI.
Use pip to install:

    $ pip install secrets-storage

Basic Usage
-----------
.. code:: python

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

License
-------

secrets-storage is developed and distributed under the Apache 2.0 license.