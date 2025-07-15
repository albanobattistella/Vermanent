from customtkinter import CTkTabview
from db.DbInterface import DbInterface
from gui.TreeviewResults import TreeviewResults


class TabsConfigurer:
    def __init__(self,
                 master,
                 language):
        self.language = language
        self.results = None

        master.grid_columnconfigure(0,
                                    weight=1)
        master.grid_columnconfigure(1,
                                    weight=1)
        master.grid_columnconfigure(2,
                                    weight=1)
        master.grid_columnconfigure(3,
                                    weight=10)

        master.grid_rowconfigure(0,
                                 weight=1)


class SearchResults(CTkTabview):
    def __init__(self,
                 master,
                 evidence,
                 case_name,
                 language,
                 evidence_path,
                 **kwargs):
        super().__init__(master,
                         **kwargs)
        self.evidence_path = evidence_path
        self.language = language
        self.case_name = case_name
        self.evidence = evidence
        self.db_interface = DbInterface()

        self.add("Average Similarity")
        self.add("Window Similarity")
        self.add("Word Similarity")
        self.average_tab_labels = TabsConfigurer(self.tab("Average Similarity"),
                                                 self.language)
        self.word_tab_labels = TabsConfigurer(self.tab("Word Similarity"),
                                              self.language)
        self.window_tab_labels = TabsConfigurer(self.tab("Window Similarity"),
                                                self.language)

        self.treeview_average = TreeviewResults(master=self.tab("Average Similarity"),
                                                evidence_path=self.evidence_path,
                                                language=self.language,
                                                db=self.db_interface,
                                                evidence=self.evidence,
                                                case_name=self.case_name)
        self.treeview_window = TreeviewResults(master=self.tab("Window Similarity"),
                                               evidence_path=self.evidence_path,
                                               language=self.language,
                                               db=self.db_interface,
                                               evidence=self.evidence,
                                               case_name=self.case_name)
        self.treeview_word = TreeviewResults(master=self.tab("Word Similarity"),
                                             evidence_path=self.evidence_path,
                                             language=self.language,
                                             db=self.db_interface,
                                             evidence=self.evidence,
                                             case_name=self.case_name)

    def display(self):
        self.grid(row=7,
                  column=0,
                  columnspan=7,
                  sticky="news",
                  padx=10,
                  pady=10)

    def hide(self):
        self.grid_forget()

    def update_evidence(self,
                        master,
                        evidence,
                        case_name,
                        language,
                        evidence_path):
        self.master = master
        self.evidence_path = evidence_path
        self.language = language
        self.case_name = case_name
        self.evidence = evidence
        self.treeview_window.update_evidence(evidence_path=evidence_path)
        self.treeview_word.update_evidence(evidence_path=evidence_path)
        self.treeview_average.update_evidence(evidence_path=evidence_path)

    def clear_results(self):
        self.treeview_word.delete_results()
        self.treeview_window.delete_results()
        self.treeview_average.delete_results()

    def print_results(self):
        average_results = self.db_interface.get_current_average_similarity_search(case_name=self.case_name,
                                                                                  evidence=self.evidence)
        word_results = self.db_interface.get_current_word_similarity_search(case_name=self.case_name,
                                                                            evidence=self.evidence)
        window_results = self.db_interface.get_current_window_similarity_search(case_name=self.case_name,
                                                                                evidence=self.evidence)
        if len(window_results) > 0:
            self.treeview_window.print_results(window_results)
        if len(average_results) > 0:
            self.treeview_average.print_results(average_results)
        if len(word_results) > 0:
            self.treeview_word.print_results(word_results)

    def update_app_language(self,
                            language):
        self.language = language
        self.treeview_window.update_app_language(language)
        self.treeview_word.update_app_language(language)
        self.treeview_average.update_app_language(language)
