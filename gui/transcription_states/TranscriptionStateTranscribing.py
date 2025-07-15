from customtkinter import END
from gui.transcription_states.TranscriptionState import TranscriptionState


class TranscriptionStateTranscribing(TranscriptionState):

    def disable_search(self):
        self.search_button.configure(state="disabled")
        self.search_entry.configure(state="disabled")
        self.search_entry.delete(0, END)

    def update_widgets(self):
        self.grid_widgets_forget()
        t_status = self.language["transcribing"]
        t_color = "white"
        self.disable_search()
        self.transcription_status_data_label.configure(text=t_status)
        self.transcription_status_data_label.configure(text_color=t_color)
        self.transcription_button.configure(state="disabled",
                                            text_color_disabled="white",
                                            fg_color="grey")
        self.stop_transcription_button.configure(state="normal")
        self.stop_transcription_button.grid(row=4,
                                            column=4,
                                            columnspan=3,
                                            sticky="e",
                                            padx=10,
                                            pady=10)
        self.transcriptions_status_bar.grid(row=4,
                                            column=4,
                                            columnspan=3,
                                            sticky="nw",
                                            padx=10,
                                            pady=10)
        self.transcriptions_status_bar.start()

    def update_app_language(self, language):
        self.language = language
        self.stop_transcription_button.configure(text=self.language["stop"])
        t_status = self.language["transcribing"]
        self.transcription_status_data_label.configure(text=t_status)
