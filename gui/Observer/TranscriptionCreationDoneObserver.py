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
                 evidence_data_state_new,
                 get_already_analyzed_size,
                 get_size,
                 number_analyzed_files_label,
                 language,
                 take_files):
        self.language = language
        self.number_analyzed_files_label = number_analyzed_files_label
        self.get_size = get_size
        self.get_already_analyzed_size = get_already_analyzed_size
        self.take_files = take_files
        self.get_transcription_state = get_transcription_state
        self.set_transcription_state = set_transcription_state
        self.set_evidence_data_state = set_evidence_data_state
        self.evidence_data_state_new = evidence_data_state_new
        self.transcription_state_new = transcription_state_new

    def update(self, subject: Subject) -> None:
        self.set_transcription_state(self.transcription_state_new)
        self.set_evidence_data_state(self.evidence_data_state_new)
        self.take_files()
        self.number_analyzed_files_label.configure(text=f'{self.get_already_analyzed_size()}'
                                                            f'/{self.get_size()} '
                                                            f'{self.language["analyzed_files"]}')
        self.get_transcription_state().update_widgets()

