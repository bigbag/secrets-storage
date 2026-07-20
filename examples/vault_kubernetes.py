"""Read a secret from Kubernetes-authenticated HashiCorp Vault."""

import os

from secrets_storage import ENVStorage, Secrets, VaultStorage


def main() -> None:
    vault = VaultStorage(
        host=os.environ["VAULT_ADDR"],
        namespace=os.environ["VAULT_NAMESPACE"],
        role=os.environ["VAULT_ROLE"],
        kv_version=os.environ.get("VAULT_KV_VERSION", "v2"),
    )
    secrets = Secrets([vault, ENVStorage()])
    print(secrets.get("API_TOKEN"))


if __name__ == "__main__":
    main()
