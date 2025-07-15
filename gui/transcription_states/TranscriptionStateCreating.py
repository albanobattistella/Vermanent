from customtkinter import END

from gui.transcription_states.TranscriptionState import TranscriptionState


class TranscriptionStateCreating(TranscriptionState):
    def disable_search(self):
        self.search_button.configure(state="disabled")
        self.search_entry.configure(state="disabled")
        self.search_entry.delete(0, END)

    def update_widgets(self):
        self.grid_widgets_forget()
        self.number_analyzed_files_label.configure(text="")
        t_status = self.language["creating"]
        t_color = "#ff3131"
        self.transcription_button.configure(state="disabled")
        self.transcription_status_data_label.configure(text=t_status)
        self.transcription_status_data_label.configure(text_color=t_color)
        self.disable_search()

    def update_app_language(self, language):
        self.language = language
        self.stop_transcription_button.configure(text=self.language["stop"])
        t_status = self.language["todo"]
        self.transcription_status_data_label.configure(text=t_status)