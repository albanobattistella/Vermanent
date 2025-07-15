from threading import Thread
from search.SearchSyncData import SearchSyncData
from gui.Observer.SearchFinishedObserver import Observer
from gui.Observer.Subject import Subject


class Calculator(Thread, Subject):
    def __init__(self,
                 search_sync_data: SearchSyncData,
                 searched_text: str,
                 evidence,
                 case_name,
                 db):
        Thread.__init__(self)
        self._window_length = 5
        self._search_done_observers = []
        self.case_name = case_name
        self.evidence = evidence
        self.db = db
        self._search_sync_data = search_sync_data
        self.searched_text = searched_text

    def attach(self, observer: Observer) -> None:
        self._search_done_observers.append(observer)

    def detach(self, observer: Observer) -> None:
        self._search_done_observers.remove(observer)

    def notify(self) -> None:
        for observer in self._search_done_observers:
            observer.update(self)

    def calculate_average_similarity(self,
                                     nlp_searched_text,
                                     nlp_audio_text):
        return round(((nlp_searched_text.similarity(nlp_audio_text) + 1) / 2) * 100, 2)

    def calculate_window_similarity(self,
                                    nlp_searched_text,
                                    nlp_audio_text):

        max_similarity = -2
        audio_tokens_list = []
        [audio_tokens_list.append(token) for token in nlp_audio_text]

        if len(audio_tokens_list) < self._window_length:
            similarity = nlp_audio_text.similarity(nlp_searched_text)
            return round(similarity * 100, 2)
        else:
            number_of_windows = len(audio_tokens_list) - self._window_length + 1
            for i in range(0, number_of_windows):
                similarity = nlp_searched_text.similarity(nlp_audio_text[i:self._window_length + i - 1])
                if similarity > max_similarity:
                    max_similarity = similarity
            return round(((max_similarity + 1) / 2) * 100, 2)

    def calculate_word_similarity(self,
                                  nlp_searched_text,
                                  nlp_audio_text):
        max_similarity = 0

        for token in nlp_audio_text:
            similarity = token.similarity(nlp_searched_text)
            if similarity > max_similarity:
                max_similarity = similarity
        return round(((max_similarity + 1) / 2) * 100, 2)

    def run(self):
        file = self._search_sync_data.get_from_to_analyze_queue()
        while file is not None:
            nlp_audio = file["nlp"]
            nlp_searched_text = file["nlp_searched_text"]

            if nlp_audio is not None and nlp_searched_text is not None:
                average_similarity = self.calculate_average_similarity(nlp_searched_text=nlp_searched_text,
                                                                       nlp_audio_text=nlp_audio)
                word_similarity = self.calculate_word_similarity(nlp_searched_text=nlp_searched_text,
                                                                 nlp_audio_text=nlp_audio)
                window_similarity = self.calculate_window_similarity(nlp_searched_text=nlp_searched_text,
                                                                     nlp_audio_text=nlp_audio)

            else:
                average_similarity = "No data"
                word_similarity = "No data"
                window_similarity = "No data"

            self.db.insert_similarities(self.case_name,
                                        self.evidence,
                                        file["id"],
                                        average_similarity,
                                        window_similarity,
                                        word_similarity)
            file = self._search_sync_data.get_from_to_analyze_queue()

        self._search_sync_data.put_on_analyzed_queue(None)
        self.notify()
