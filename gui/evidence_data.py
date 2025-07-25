import threading
from transcription.TranscriptionSyncData import TranscriptionSyncData
from gui.Observer.Subject import Subject
from gui.Observer.TranscriptionCreationDoneObserver import Observer


class EvidenceData(Subject):
    def __init__(self,
                 language,
                 evidence_data,
                 case_name,
                 db):
        Subject.__init__(self)
        self.db = db
        self._observers = []
        self.gui_interface = None
        self.case_name = case_name
        self.evidence = evidence_data["evidence"]
        self.path = evidence_data["files_path"]
        self.state = evidence_data["transcriptions"]
        if self.state == "creating":
            thread_creating = threading.Thread(target=self.insert_evidence_files_path)
            thread_creating.start()

        self.sync_data = TranscriptionSyncData(files_directory=self.path,
                                               case_name=self.case_name,
                                               evidence=self.evidence)
        self.search_state = None
        self.language = language
        self.transcription_manager = None
        self.transcribers = None
        self.preprocessors = []
        self.calculator = None

    def set_state(self,
                  state):
        self.state = state

    def set_search_state(self,
                         state):
        self.search_state = state

    def insert_evidence_files_path(self):
        self.db.insert_evidence_files_path(case_name=self.case_name,
                                           evidence=self.evidence,
                                           files_path=self.path)
        self.state = "todo"
        self.notify()

    def attach(self, observer: Observer) -> None:
        self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        self._observers.remove(observer)

    def notify(self) -> None:
        for observer in self._observers:
            observer.update(self)
