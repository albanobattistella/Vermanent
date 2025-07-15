from customtkinter import END

from gui.transcription_states.TranscriptionState import TranscriptionState


class TranscriptionStateToDo(TranscriptionState):
    def disable_search(self):
        self.search_button.configure(state="disabled")
        self.search_entry.configure(state="disabled")
        self.search_entry.delete(0, END)

    def enable_search(self):
        self.search_button.configure(state="normal")
        self.search_entry.configure(state="normal")

    def update_widgets(self):
        self.grid_widgets_forget()
        t_status = self.language["todo"]
        t_color = "#ff3131"
        self.transcription_button.configure(state="normal",
                                            fg_color="#619B8A")
        self.transcription_status_data_label.configure(text=t_status)
        self.transcription_status_data_label.configure(text_color=t_color)
        self.transcription_button.configure(state="normal")
        self.transcriptions_status_bar.stop()
        self.transcriptions_status_bar.grid_forget()
        self.stop_transcription_button.grid_forget()
        self.enable_search()

    def update_app_language(self, language):
        self.language = language
        self.stop_transcription_button.configure(text=self.language["stop"])
        t_status = self.language["todo"]
        self.transcription_status_data_label.configure(text=t_status)