from abc import ABC, abstractmethod


class Subject(ABC):
    def __init__(self):
        self._size = None

    @abstractmethod
    def attach(self, observer) -> None:
        pass

    @abstractmethod
    def detach(self, observer) -> None:
        pass

    @abstractmethod
    def notify(self) -> None:
        pass
