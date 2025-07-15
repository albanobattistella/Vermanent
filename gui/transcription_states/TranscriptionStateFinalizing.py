from customtkinter import END
from gui.transcription_states.TranscriptionState import TranscriptionState


class TranscriptionStateFinalizing(TranscriptionState):

    def disable_search(self):
        self.search_button.configure(state="disabled")
        self.search_entry.configure(state="disabled")
        self.search_entry.delete(0, END)

    def update_widgets(self):
        self.grid_widgets_forget()
        t_status = self.language["finalizing"]
        t_color = "red"
        self.disable_search()
        self.transcription_button.configure(state="disabled",
                                            text_color_disabled="white",
                                            fg_color="grey")
        self.transcription_status_data_label.configure(text=t_status)
        self.transcription_status_data_label.configure(text_color=t_color)
        self.transcriptions_status_bar.stop()
        self.transcriptions_status_bar.grid_forget()
        self.stop_transcription_button.grid_forget()

    def update_app_language(self, language):
        self.language = language
        self.stop_transcription_button.configure(text=self.language["stop"])
        t_status = self.language["finalizing"]
        self.transcription_status_data_label.configure(text=t_status)
