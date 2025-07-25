import json
import os

from customtkinter import CTkLabel, CTkButton, CTkProgressBar, CTkEntry, CTkComboBox
from db.DbInterface import DbInterface
from search.Calculator import Calculator
from search.Preprocessor import Preprocessor
from gui.evidence_data import EvidenceData
from gui.SearchResults import SearchResults
from gui.transcription_states.TranscriptionStateCreating import TranscriptionStateCreating
from gui.transcription_states.TranscriptionStateDone import TranscriptionStateDone
from gui.transcription_states.TranscriptionStateToDo import TranscriptionStateToDo
from gui.transcription_states.TranscriptionStateTranscribing import TranscriptionStateTranscribing
from gui.transcription_states.TranscriptionStateFinalizing import TranscriptionStateFinalizing
from search.GuiInterface import GuiInterface
from search.SearchSyncData import SearchSyncData
from transcription.DataStorageManager import DataStorageManager
from transcription.Transcriber import Transcriber
from gui.Observer.AnalyzedFilesObserver import ConcreteObserver as AnalyzedFilesObserver
from gui.Observer.TranscriptionStateObserver import ConcreteObserver as TranscriptionStateObserver
from gui.Observer.TranscriptionCreationDoneObserver import ConcreteObserver as TranscriptionCreationDoneObserver
from gui.Observer.SearchFinishedObserver import ConcreteObserver as SearchFinishedObserver


class EvidenceView:
    def __init__(self,
                 master,
                 root,
                 language,
                 evidence_data,
                 case_name,
                 db: DbInterface):

        self.search_status_bar = None
        self.transcription_status_data_label = None
        self.last_search_label = None
        self.last_search_header_label = None
        self.search_language_dropdown = None
        self.search_button = None
        self.transcription_creation_done_observer = None
        self.search_entry = None
        self.search_label = None
        self.transcription_language_dropdown = None
        self.transcription_button = None
        self.transcription_status_label = None
        self.path_label = None
        self.path_name_label = None
        self.number_analyzed_files_label = None
        self.transcriptions_status_bar = None
        self.stop_transcription_button = None
        self.transcription_state = None
        self.root = root
        self.evidence_data = EvidenceData(language, evidence_data, case_name, db)
        self.db = db
        self.language = language
        self.master = master

        self.create_widgets()
        self.set_initial_state()

        self.search_results = SearchResults(self.master,
                                            segmented_button_selected_color="#619B8A",
                                            segmented_button_selected_hover_color="#3c6c5e",
                                            text_color="gray5",
                                            evidence=self.evidence_data.evidence,
                                            case_name=self.evidence_data.case_name,
                                            language=self.language,
                                            evidence_path=self.evidence_data.path)

        label = self.number_analyzed_files_label

        # OBSERVERS
        self.transcription_state_done_observer = TranscriptionStateObserver(
            set_transcription_state=self.set_transcription_state,
            transcription_state_new=TranscriptionStateDone(transcriptions_status_bar=self.transcriptions_status_bar,
                                                           stop_transcription_button=self.stop_transcription_button,
                                                           transcription_status_data_label=self.transcription_status_data_label,
                                                           transcription_button=self.transcription_button,
                                                           search_button=self.search_button,
                                                           search_entry=self.search_entry,
                                                           language=self.language,
                                                           number_analyzed_files_label=self.number_analyzed_files_label),
            set_evidence_data_state=self.evidence_data.set_state,
            evidence_data_state_new="done",
            get_transcription_state=self.get_transcription_state
        )
        self.transcription_state_todo_observer = TranscriptionStateObserver(
            set_transcription_state=self.set_transcription_state,
            transcription_state_new=TranscriptionStateToDo(transcriptions_status_bar=self.transcriptions_status_bar,
                                                           stop_transcription_button=self.stop_transcription_button,
                                                           transcription_status_data_label=self.transcription_status_data_label,
                                                           transcription_button=self.transcription_button,
                                                           search_button=self.search_button,
                                                           search_entry=self.search_entry,
                                                           language=self.language,
                                                           number_analyzed_files_label=self.number_analyzed_files_label),
            set_evidence_data_state=self.evidence_data.set_state,
            evidence_data_state_new="todo",
            get_transcription_state=self.get_transcription_state)

        self.analyzed_file_observer = AnalyzedFilesObserver(language=self.language)
        self.search_finished_observer = SearchFinishedObserver()

        # ATTACH OBSERVERS
        self.evidence_data.sync_data.attach(self.transcription_state_done_observer)
        self.evidence_data.sync_data.attach_number_files_observer(self.analyzed_file_observer)
        self.analyzed_file_observer.set_label(label)

        self.evidence_data.gui_interface = GuiInterface(self.search_results)
        self.search_finished_observer.set_status_bar(self.search_status_bar)
        self.search_finished_observer.set_evidence_data(self.evidence_data)
        self.search_finished_observer.set_gui_interface(self.evidence_data.gui_interface)

        if self.evidence_data.search_state is True:
            self.search_results.print_results()

    def get_transcription_state(self):
        return self.transcription_state

    def set_transcription_state(self, transcription_state):
        self.transcription_state = transcription_state

    def set_initial_state(self):
        if self.evidence_data.state == "creating":
            self.transcription_state = TranscriptionStateCreating(
                transcriptions_status_bar=self.transcriptions_status_bar,
                stop_transcription_button=self.stop_transcription_button,
                transcription_status_data_label=self.transcription_status_data_label,
                transcription_button=self.transcription_button,
                search_button=self.search_button,
                search_entry=self.search_entry,
                language=self.language,
                number_analyzed_files_label=self.number_analyzed_files_label)
            self.transcription_creation_done_observer = TranscriptionCreationDoneObserver(
                set_transcription_state=self.set_transcription_state,
                transcription_state_new=TranscriptionStateToDo(transcriptions_status_bar=self.transcriptions_status_bar,
                                                               stop_transcription_button=self.stop_transcription_button,
                                                               transcription_status_data_label=self.transcription_status_data_label,
                                                               transcription_button=self.transcription_button,
                                                               search_button=self.search_button,
                                                               search_entry=self.search_entry,
                                                               language=self.language,
                                                               number_analyzed_files_label=self.number_analyzed_files_label),
                set_evidence_data_state=self.evidence_data.set_state,
                evidence_data_state_new="todo",
                get_transcription_state=self.get_transcription_state,
                get_already_analyzed_size=self.evidence_data.sync_data.get_already_analyzed_size,
                get_size=self.evidence_data.sync_data.get_size,
                take_files=self.evidence_data.sync_data.take_files,
                number_analyzed_files_label=self.number_analyzed_files_label,
                language=self.language)
            self.evidence_data.attach(self.transcription_creation_done_observer)
        elif self.evidence_data.state == "todo":
            self.transcription_state = TranscriptionStateToDo(transcriptions_status_bar=self.transcriptions_status_bar,
                                                              stop_transcription_button=self.stop_transcription_button,
                                                              transcription_status_data_label=self.transcription_status_data_label,
                                                              transcription_button=self.transcription_button,
                                                              search_button=self.search_button,
                                                              search_entry=self.search_entry,
                                                              language=self.language,
                                                              number_analyzed_files_label=self.number_analyzed_files_label)
            self.evidence_data.sync_data.take_files()
            self.number_analyzed_files_label.configure(
                text=f'{self.evidence_data.sync_data.get_already_analyzed_size()}'
                     f'/{self.evidence_data.sync_data.get_size()} '
                     f'{self.language["analyzed_files"]}')
        elif self.evidence_data.state == "done":
            self.transcription_state = TranscriptionStateDone(transcriptions_status_bar=self.transcriptions_status_bar,
                                                              stop_transcription_button=self.stop_transcription_button,
                                                              transcription_status_data_label=self.transcription_status_data_label,
                                                              transcription_button=self.transcription_button,
                                                              search_button=self.search_button,
                                                              search_entry=self.search_entry,
                                                              language=self.language,
                                                              number_analyzed_files_label=self.number_analyzed_files_label)
        self.transcription_state.update_widgets()

    def create_widgets(self):
        self.stop_transcription_button = CTkButton(self.master,
                                                   text=self.language["stop"],
                                                   text_color="#ff3131",
                                                   command=self.stop_transcriptions,
                                                   state="disabled",
                                                   width=150,
                                                   fg_color="transparent",
                                                   hover_color="dark red",
                                                   border_color="#ff3131",
                                                   border_width=2)
        self.transcriptions_status_bar = CTkProgressBar(self.master,
                                                        mode="indeterminate",
                                                        width=200)
        self.number_analyzed_files_label = CTkLabel(self.master,
                                                    text="",
                                                    fg_color="transparent",
                                                    bg_color="transparent")

        self.path_name_label = CTkLabel(self.master,
                                        text=self.language["evidence_path"],
                                        text_color="#619B8A")

        self.path_label = CTkLabel(self.master,
                                   text=self.evidence_data.path)

        self.transcription_status_label = CTkLabel(self.master,
                                                   text=self.language["transcription_status"],
                                                   text_color="#619B8A",
                                                   height=10)

        self.transcription_button = CTkButton(master=self.master,
                                              text=self.language["start_transcribing"],
                                              command=self.start_transcribe)

        # Search for available languages
        self.transcription_language_dropdown = CTkComboBox(self.master)
        with open("search/languages.json", "r") as file:
            languages = json.load(file)
        languages = languages.items()
        temp = []
        for lang in languages:
            temp.append(lang[0])
        temp.append("Multilanguage")
        del languages
        self.transcription_language_dropdown.configure(values=temp)
        self.transcription_language_dropdown.set(value=temp[0])

        self.search_label = CTkLabel(master=self.master,
                                     text=self.language["search"],
                                     text_color="#619B8A")

        self.search_entry = CTkEntry(master=self.master,
                                     state="disabled")

        self.search_button = CTkButton(master=self.master,
                                       text=self.language["start_searching"],
                                       state="disabled",
                                       command=self.start_search)

        temp.remove("Multilanguage")
        self.search_language_dropdown = CTkComboBox(self.master)
        self.search_language_dropdown.configure(values=temp)
        self.search_language_dropdown.set(value=temp[0])

        self.last_search_header_label = CTkLabel(master=self.master,
                                                 text=self.language["last_search"] + ":",
                                                 text_color="#619B8A")

        last_search = self.db.get_last_search(case_name=self.evidence_data.case_name,
                                              evidence=self.evidence_data.evidence)
        if last_search is None:
            last_search = self.language["no_previous_search"]
            self.evidence_data.set_search_state(False)
        else:
            self.evidence_data.set_search_state(True)
        self.last_search_label = CTkLabel(master=self.master,
                                          text=last_search)

        self.transcription_status_data_label = CTkLabel(self.master,
                                                        wraplength=100,
                                                        width=200,
                                                        fg_color="transparent")

        self.search_status_bar = CTkProgressBar(self.master,
                                                width=200,
                                                mode="indeterminate")

    def display(self):
        self.number_analyzed_files_label.grid(row=4,
                                              column=4,
                                              sticky="sw",
                                              padx=10,
                                              pady=5)
        self.path_name_label.grid(row=3,
                                  column=0,
                                  sticky="w",
                                  padx=10,
                                  pady=10)
        self.path_label.grid(row=3,
                             column=1,
                             columnspan=3,
                             sticky="w",
                             padx=10,
                             pady=10)
        self.transcription_status_label.grid(row=4,
                                             column=0,
                                             sticky="w",
                                             padx=10,
                                             pady=10)
        self.transcription_button.grid(row=4,
                                       column=2,
                                       sticky="nw",
                                       padx=10,
                                       pady=10)
        self.search_label.grid(row=5,
                               column=0,
                               sticky="w",
                               padx=10,
                               pady=10)
        self.transcription_language_dropdown.grid(row=4,
                                                  column=3,
                                                  sticky="w")
        self.search_language_dropdown.grid(row=5,
                                           column=4,
                                           sticky="w")
        self.search_entry.grid(row=5,
                               column=1,
                               columnspan=2,
                               sticky="we",
                               padx=10,
                               pady=10)
        self.search_button.grid(row=5,
                                column=3,
                                sticky="w",
                                padx=10,
                                pady=10)
        self.last_search_header_label.grid(row=6,
                                           column=0,
                                           sticky="w",
                                           padx=10,
                                           pady=10)
        self.last_search_label.grid(row=6,
                                    column=1,
                                    sticky="w",
                                    columnspan=2,
                                    padx=10,
                                    pady=10)
        self.transcription_status_data_label.grid(row=4,
                                                  column=1,
                                                  sticky="w",
                                                  padx=10,
                                                  pady=10)
        self.transcription_state.update_widgets()
        self.search_results.display()

    def hide(self):
        self.number_analyzed_files_label.grid_forget()
        self.path_name_label.grid_forget()
        self.path_label.grid_forget()
        self.transcriptions_status_bar.grid_forget()
        self.stop_transcription_button.grid_forget()
        self.transcription_status_label.grid_forget()
        self.transcription_button.grid_forget()
        self.search_label.grid_forget()
        self.transcription_language_dropdown.grid_forget()
        self.search_language_dropdown.grid_forget()
        self.search_entry.grid_forget()
        self.search_button.grid_forget()
        self.last_search_header_label.grid_forget()
        self.last_search_label.grid_forget()
        self.transcription_status_data_label.grid_forget()
        self.search_status_bar.grid_forget()
        self.search_results.hide()

    def stop_transcriptions(self):
        self.evidence_data.transcribers.stop()
        self.evidence_data.set_state("finalizing")
        self.transcription_state = TranscriptionStateFinalizing(
            transcriptions_status_bar=self.transcriptions_status_bar,
            stop_transcription_button=self.stop_transcription_button,
            transcription_status_data_label=self.transcription_status_data_label,
            transcription_button=self.transcription_button,
            search_button=self.search_button,
            search_entry=self.search_entry,
            language=self.language,
            number_analyzed_files_label=self.number_analyzed_files_label)
        self.transcription_state.update_widgets()

    def start_transcribe(self):
        self.evidence_data.set_state("transcribing")
        self.transcription_state = TranscriptionStateTranscribing(
            transcriptions_status_bar=self.transcriptions_status_bar,
            stop_transcription_button=self.stop_transcription_button,
            transcription_status_data_label=self.transcription_status_data_label,
            transcription_button=self.transcription_button,
            search_button=self.search_button,
            search_entry=self.search_entry,
            language=self.language,
            number_analyzed_files_label=self.number_analyzed_files_label)
        self.transcription_state.update_widgets()
        op_language = self.transcription_language_dropdown.get()
        self.evidence_data.transcribers = Transcriber(self.evidence_data.sync_data,
                                                      model=self.root.model,
                                                      semaphore=self.root.semaphore,
                                                      transcriptions_language=op_language,
                                                      )
        self.evidence_data.transcribers.attach(self.transcription_state_todo_observer)
        self.evidence_data.transcriptions_manager = DataStorageManager(self.evidence_data.sync_data)
        self.evidence_data.transcriptions_manager.start()
        self.evidence_data.transcribers.start()

    def start_search(self):
        searched_text = self.search_entry.get()
        self.evidence_data.search_state = "searching"
        searched_text_lang = self.search_language_dropdown.get()
        # number_of_workers = os.cpu_count() - 6
        number_of_workers = 4
        self.search_status_bar.grid(row=5,
                                    column=5,
                                    columnspan=2,
                                    pady=10)
        self.db.put_last_search(case_name=self.evidence_data.case_name,
                                evidence=self.evidence_data.evidence,
                                last_search=searched_text)
        self.last_search_label.configure(text=searched_text)
        data = self.db.take_transcribed_text(case_name=self.evidence_data.case_name,
                                             evidence=self.evidence_data.evidence)
        if number_of_workers < 2:
            number_of_workers = 2
        section_number = int(len(data) / (number_of_workers - 1))
        sync_data = SearchSyncData(self.evidence_data.case_name,
                                   self.evidence_data.evidence)
        for i in range(0, number_of_workers - 1):
            if i == number_of_workers - 1:
                self.evidence_data.preprocessors.append(Preprocessor(case_name=self.evidence_data.case_name,
                                                                     evidence=self.evidence_data.evidence,
                                                                     searched_text=searched_text,
                                                                     searched_text_lang=searched_text_lang,
                                                                     sync_data=sync_data,
                                                                     db=self.db,
                                                                     data=data[i * section_number:]))
            else:
                self.evidence_data.preprocessors.append(Preprocessor(case_name=self.evidence_data.case_name,
                                                                     evidence=self.evidence_data.evidence,
                                                                     searched_text=searched_text,
                                                                     searched_text_lang=searched_text_lang,
                                                                     sync_data=sync_data,
                                                                     db=self.db,
                                                                     data=data[i * section_number:
                                                                               i * section_number + section_number]))

        calculator = Calculator(case_name=self.evidence_data.case_name,
                                evidence=self.evidence_data.evidence,
                                searched_text=searched_text,
                                search_sync_data=sync_data,
                                db=self.db)
        calculator.attach(self.search_finished_observer)
        self.evidence_data.calculator = calculator
        for p in self.evidence_data.preprocessors:
            p.start()
        calculator.start()
        self.search_status_bar.start()

    def update_app_language(self,
                            language):
        self.path_name_label.configure(text=language["evidence_path"])
        self.transcription_status_label.configure(text=language["transcription_status"])
        self.transcription_button.configure(text=language["start_transcribing"])
        self.search_label.configure(text=language["search"])
        self.transcription_state.update_app_language(language=language)
        self.search_button.configure(text=language["start_searching"])
        self.last_search_header_label.configure(text=language["last_search"] + ":")
        if self.evidence_data.state != "creating":
            already_analyzed_number = self.evidence_data.sync_data.get_already_analyzed_size()
            total_number_of_files = self.evidence_data.sync_data.get_size()
            label_text = str(already_analyzed_number) + "/" + str(total_number_of_files) + " " + language[
                "analyzed_files"]
            self.number_analyzed_files_label.configure(text=label_text)
        if self.last_search_label.cget("text") == self.language["no_previous_search"]:
            self.last_search_label.configure(text=language["no_previous_search"])
        self.language = language
        self.search_results.update_app_language(language)
