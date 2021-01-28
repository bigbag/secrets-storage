import pytest
from mock import patch

from secrets_storage import ENVStorage, Secrets


class TestSecrets:
    def test_if_not_found_storage(self):
        secrets = Secrets(storages=[])
        with pytest.raises(ValueError):
            secrets.get("DEMO")

    def test_if_all_storages_disable(self):
        secrets = Secrets(storages=[ENVStorage(available=False)])
        with pytest.raises(ValueError):
            secrets.get("DEMO")


class TestENVStorage:
    @patch("os.getenv")
    def test_success(self, mock_getenv):
        secrets = Secrets(storages=[ENVStorage()])

        mock_getenv.return_value = "Test"
        assert secrets.get("DEMO") == "Test"

    def test_if_not_found(self):
        secrets = Secrets(storages=[ENVStorage()])
        with pytest.raises(ValueError):
            secrets.get("DEMO")

    def test_if_not_found_with_fallback_value(self):
        secrets = Secrets(storages=[ENVStorage()])
        assert secrets.get("DEMO", "Test") == "Test"
