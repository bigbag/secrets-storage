import abc
from typing import Any, Optional


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
