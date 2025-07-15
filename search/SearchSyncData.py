from db.DbInterface import DbInterface
from threading import Semaphore


class SearchSyncData:

    def __init__(self, case_name, evidence):
        self._evidence = evidence
        self._case_name = case_name
        self._db_interface = DbInterface()

        self._to_analyze_queue_mutex = Semaphore(0)
        self._analyzed_queue_mutex = Semaphore(1)
        self._taker_mutex = Semaphore(0)
        self._searcher_mutex = Semaphore(1)

        self._to_analyze_queue = []
        self._analyzed_queue = []

    def set_to_analyze_queue(self, data):
        self._to_analyze_queue = data
        self._to_analyze_queue_mutex.release(len(data))

    def get_from_to_analyze_queue(self):
        self._searcher_mutex.acquire()
        self._to_analyze_queue_mutex.acquire()
        data = self._to_analyze_queue.pop(0)
        self._searcher_mutex.release()
        return data

    def put_on_analyzed_queue(self, data):
        self._analyzed_queue_mutex.acquire()
        self._analyzed_queue.append(data)
        self._taker_mutex.release()
        self._analyzed_queue_mutex.release()

    def get_from_analyzed_queue(self):
        self._taker_mutex.acquire()
        data = self._analyzed_queue.pop(0)
        return data

    def put_on_to_analyze_queue(self, data):
        self._to_analyze_queue.append(data)
        self._to_analyze_queue_mutex.release()
