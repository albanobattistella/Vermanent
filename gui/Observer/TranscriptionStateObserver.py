from abc import ABC
from gui.Observer.Subject import Subject


class Observer(ABC):
    def update(self, subject: Subject) -> None:
        pass


class ConcreteObserver(Observer):
    def __init__(self,
                 set_transcription_state,
                 transcription_state_new,
                 get_transcription_state,
                 set_evidence_data_state,
                 evidence_data_state_new):
        self.get_transcription_state = get_transcription_state
        self.set_transcription_state = set_transcription_state
        self.set_evidence_data_state = set_evidence_data_state
        self.evidence_data_state_new = evidence_data_state_new

        self.transcription_state_new = transcription_state_new

    def update(self, subject: Subject) -> None:
        self.set_transcription_state(self.transcription_state_new)
        self.set_evidence_data_state(self.evidence_data_state_new)
        self.get_transcription_state().update_widgets()

