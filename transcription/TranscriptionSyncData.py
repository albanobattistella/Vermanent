from threading import Semaphore
from db.DbInterface import DbInterface
from gui.Observer.AnalyzedFilesObserver import Observer
from gui.Observer.Subject import Subject
from gui.Observer.Subject_number_files import SubjectNumberFiles


class TranscriptionSyncData(Subject, SubjectNumberFiles):

    def __init__(self,
                 files_directory,
                 case_name,
                 evidence):
        Subject.__init__(self)

        self._number_analyzed_files_observers = []
        self._observers = []
        self.set_state_mutex = Semaphore(0)
        self._evidence = evidence
        self._db = DbInterface()
        self._case_name = case_name
        self._files_directory = files_directory
        self._files = []
        self._queue = []
        self._stop = False
        self._queue_mutex_db = Semaphore(0)
        self._queue_mutex_transcription = Semaphore(1)
        self._files_mutex = Semaphore(1)
        self._size = 0
        self._already_analyzed_number = 0

    def put_on_queue(self, data):
        self._queue_mutex_transcription.acquire()
        self._queue.append(data)
        self._queue_mutex_db.release()
        self._queue_mutex_transcription.release()

    def get_from_queue(self):
        self._queue_mutex_db.acquire()
        try:
            data = self._queue.pop(0)
            if data is not None:
                self._already_analyzed_number += 1
                self.notify_number_files_observer()
        except IndexError:
            data = None
        if self._already_analyzed_number == self._size:
            self._db.change_transcription_status(case_name=self._case_name,
                                                 evidence=self._evidence,
                                                 status="done")
            self.notify()
        return data

    def take_files(self):
        files, to_analyze, size = self._db.take_files_to_transcribe_with_size(case_name=self._case_name,
                                                                              evidence=self._evidence)
        self._files = files
        self._size = size
        self._already_analyzed_number = self._size - to_analyze

    def get_file(self):
        self._files_mutex.acquire()
        try:
            file = self._files.pop(0)
        except IndexError:
            self._files_mutex.release()
            return None
        self._files_mutex.release()
        return [self._files_directory + "/", file]

    def get_case_name(self):
        case_name = self._case_name
        return case_name

    def get_evidence(self):
        evidence = self._evidence
        return evidence

    def get_size(self):
        size = self._size
        return size

    def get_already_analyzed_size(self):
        size = self._already_analyzed_number
        return size

    def set_state(self,
                  already_analyzed):
        for file in already_analyzed:
            self._files.remove(file)
        self.set_state_mutex.release()

    def attach(self, observer: Observer) -> None:
        self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        self._observers.remove(observer)

    def notify(self) -> None:
        for observer in self._observers:
            observer.update(self)

    def attach_number_files_observer(self, observer) -> None:
        self._number_analyzed_files_observers.append(observer)

    def detach_number_files_observer(self, observer) -> None:
        self._number_analyzed_files_observers.remove(observer)

    def notify_number_files_observer(self) -> None:
        for observer in self._number_analyzed_files_observers:
            observer.update(self)
