from abc import ABC, abstractmethod


class TranscriptionState(ABC):
    def __init__(self,
                 transcriptions_status_bar,
                 stop_transcription_button,
                 transcription_status_data_label,
                 transcription_button,
                 search_button,
                 search_entry,
                 language,
                 number_analyzed_files_label):
        self.number_analyzed_files_label = number_analyzed_files_label
        self.search_entry = search_entry
        self.search_button = search_button
        self.transcription_button = transcription_button
        self.language = language
        self.transcription_status_data_label = transcription_status_data_label
        self.stop_transcription_button = stop_transcription_button
        self.transcriptions_status_bar = transcriptions_status_bar

    def grid_widgets_forget(self):
        if self.transcriptions_status_bar.grid_info():
            self.transcriptions_status_bar.grid_forget()
        if self.stop_transcription_button.grid_info():
            self.stop_transcription_button.grid_forget()
    @abstractmethod
    def update_widgets(self):
        pass

    @abstractmethod
    def update_app_language(self, language):
        pass
