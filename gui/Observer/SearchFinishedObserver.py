from abc import ABC
from gui.Observer.Subject import Subject


class Observer(ABC):
    def update(self, subject: Subject) -> None:
        pass


class ConcreteObserver(Observer):
    def __init__(self):
        self._search_status_bar = None
        self._evidence_data = None
        self._gui_interface = None

    def set_status_bar(self,
                       status_bar):
        self._search_status_bar = status_bar

    def set_gui_interface(self,
                          gui_interface):
        self._gui_interface = gui_interface

    def set_evidence_data(self,
                          evidence_data):
        self._evidence_data = evidence_data

    def update(self, subject: Subject) -> None:
        self._search_status_bar.grid_forget()
        self._evidence_data.set_search_state(True)
        self._gui_interface.print_results_on_gui()
