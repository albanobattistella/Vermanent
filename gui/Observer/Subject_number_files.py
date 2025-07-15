from abc import ABC, abstractmethod


class SubjectNumberFiles(ABC):
    def __init__(self):
        self._size = None

    @abstractmethod
    def attach_number_files_observer(self, observer) -> None:
        pass

    @abstractmethod
    def detach_number_files_observer(self, observer) -> None:
        pass

    @abstractmethod
    def notify_number_files_observer(self) -> None:
        pass
