from dataclasses import dataclass
from typing import Any

import pytest

from secrets_storage import MISSING, BaseStorage, SecretNotFoundError, Secrets


@dataclass
class Storage(BaseStorage):
    name: str
    value: Any = MISSING
    available: bool = True

    @property
    def enabled(self) -> bool:
        return self.available

    def get_secret(self, name: str) -> Any:
        return self.value


@pytest.mark.parametrize("value", ["", 0, False, None])
def test_get_returns_present_falsey_values(value: Any) -> None:
    assert Secrets([Storage("first", value)]).get("API_TOKEN") is value


def test_get_uses_provider_priority() -> None:
    assert Secrets([Storage("first", "one"), Storage("second", "two")]).get("API_TOKEN") == "one"


def test_get_skips_disabled_providers() -> None:
    storages = [Storage("first", "one", available=False), Storage("second", "two")]
    assert Secrets(storages).get("API_TOKEN") == "two"


def test_get_returns_an_explicit_falsey_fallback() -> None:
    assert Secrets([Storage("first")]).get("API_TOKEN", fallback_value=False) is False


def test_get_raises_without_a_value_or_fallback() -> None:
    with pytest.raises(SecretNotFoundError, match="API_TOKEN"):
        Secrets([Storage("first")]).get("API_TOKEN")
