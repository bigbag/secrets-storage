"""Secret lookup coordination."""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from .exceptions import SecretNotFoundError
from .storages import MISSING, BaseStorage


@dataclass(frozen=True, slots=True)
class Secrets:
    """Look up a secret from enabled storages in declaration order."""

    storages: Sequence[BaseStorage]

    def get(self, name: str, fallback_value: Any = MISSING) -> Any:
        """Return a configured secret or explicit fallback.

        Values including ``None``, an empty string, ``0``, and ``False`` are
        present values; only :data:`MISSING` denotes an absent key.
        """
        for storage in self.storages:
            if storage.enabled:
                value = storage.get_secret(name)
                if value is not MISSING:
                    return value
        if fallback_value is not MISSING:
            return fallback_value
        raise SecretNotFoundError(f"Secret {name!r} was not found in an enabled storage.")
