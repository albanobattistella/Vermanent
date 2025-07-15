from gui.transcription_states.TranscriptionState import TranscriptionState


class TranscriptionStateDone(TranscriptionState):
    def enable_search(self):
        self.search_button.configure(state="normal")
        self.search_entry.configure(state="normal")
        self.transcription_button.configure(state="disabled")

    def update_widgets(self):
        self.grid_widgets_forget()
        t_status = self.language["done"]
        t_color = "light blue"
        self.transcription_status_data_label.configure(text=t_status)
        self.transcription_status_data_label.configure(text_color=t_color)
        self.transcription_button.configure(state="disabled",
                                            text_color_disabled="white",
                                            fg_color="grey")
        self.transcriptions_status_bar.stop()
        self.transcriptions_status_bar.grid_forget()
        self.stop_transcription_button.grid_forget()
        self.enable_search()

    def update_app_language(self, language):
        self.language = language
        self.stop_transcription_button.configure(text=self.language["stop"])
        t_status = self.language["done"]
        self.transcription_status_data_label.configure(text=t_status)
