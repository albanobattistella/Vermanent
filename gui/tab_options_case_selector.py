import json
import os
from tkinter import messagebox
from customtkinter import CTkButton, CTkImage, CTkFrame, CTkScrollableFrame, CTkLabel, CTkComboBox
from gui.case_view import CaseView
from PIL import Image
from os import listdir
from gui.AddCaseWindow import AddCaseWindow
from gui.empty_view import EmptyView


class CaseButton(CTkButton):
    def __init__(self,
                 master,
                 case_name,
                 **kwargs):
        super().__init__(master,
                         **kwargs)
        self.case_name = case_name
        self.configure(command=lambda: master.append_case_state(self.case_name))


def take_cases():
    cases_directory = "DB/Cases"
    files = listdir(path=cases_directory)
    result = []
    for file in files:
        result.append(file.replace(".db", ""))
    del files
    return result


class ScrollableFrameCases(CTkScrollableFrame):
    def __init__(self,
                 master,
                 root,
                 language,
                 db,
                 **kwargs):
        super().__init__(master,
                         **kwargs)
        self.db = db
        self.language = language
        self.root = root
        self.cases_button = []
        self.bins_buttons = []
        self.grid(column=0,
                  row=2,
                  sticky="news",
                  padx=10)
        self.grid_columnconfigure(0,
                                  weight=5)
        self.grid_columnconfigure(1,
                                  weight=1)
        i = 0
        for case in take_cases():
            self.add_case_button(case_name=case,
                                 row_index=i)
            i += 1
        del i

    def add_case_button(self,
                        case_name,
                        row_index):
        self.grid_rowconfigure(row_index,
                               weight=1)
        button = CaseButton(self,
                            case_name=case_name,
                            text=case_name)
        button.grid(row=row_index,
                    column=0,
                    sticky="we",
                    pady=5)
        self.cases_button.append(button)
        bin_button = CTkButton(self,
                               image=CTkImage(light_image=Image.open('Assets/recycle_bin.png'),
                                              dark_image=Image.open('Assets/recycle_bin.png'),
                                              size=(20, 20)),
                               text="",
                               width=25,
                               height=20,
                               fg_color="#ff3131",
                               hover_color="#841818")
        bin_button.configure(command=lambda: self.delete_case(case_name=case_name,
                                                              bin_button=bin_button,
                                                              case_button=button))
        bin_button.grid(row=row_index,
                        column=1,
                        sticky="e",
                        pady=5)
        self.bins_buttons.append(bin_button)

    def append_case_state(self, case_name):
        evidences = self.db.take_evidences_data(case_name=case_name)

        if self.root.current_state.__class__ is EmptyView:
            self.root.current_state.destroy()
            self.append_case(case_name=case_name,
                             evidences=evidences)
        else:
            self.root.current_state.hide()
            self.append_case(case_name=case_name,
                             evidences=evidences)

    def append_case(self,
                    case_name,
                    evidences):
        for case_view in self.root.case_views:
            if case_view.case_name == case_name:
                self.root.current_state = case_view
                self.root.current_state.display()
                return
        self.root.current_state = CaseView(master=self.root,
                                           language=self.language,
                                           case_name=case_name,
                                           db=self.db,
                                           evidences=evidences)
        self.root.case_views.append(self.root.current_state)
        self.root.current_state.display()

    def delete_case(self,
                    case_name,
                    case_button,
                    bin_button):
        case_to_eliminate = None
        for case_view in self.root.case_views:
            if case_view.case_name == case_name:
                case_to_eliminate = case_view
                break

        if case_to_eliminate is not None:
            for evidence_view in case_to_eliminate.evidences_view:
                if evidence_view.evidence_data.state in ["creating", "transcribing", "finalizing"] \
                        or evidence_view.evidence_data.search_state == "searching":
                    messagebox.showwarning(self.language["deleting_case_error"], self.language["fail_eliminate"])
                    return
        answer_yes = messagebox.askokcancel(title="",
                                            message=self.language["ask_confirm"])
        if answer_yes:
            self.root.db.delete_case(case_name=case_name)
            case_button.destroy()
            bin_button.destroy()

            if self.root.current_state.__class__ != EmptyView:
                self.root.case_views.remove(self.root.current_state)
                if self.root.current_state.case_name == case_name:
                    self.root.current_state.destroy()
                    self.root.current_state = EmptyView(master=self.root,
                                                        language=self.language)

    def update_app_language(self, language):
        self.language = language


class TabOptions(CTkFrame):
    def __init__(self,
                 master,
                 whisper_model,
                 app_mode,
                 root,
                 db,
                 language,
                 **kwargs):
        super().__init__(master,
                         **kwargs)

        self.app_mode = app_mode
        self.db = db
        self.root = root
        self.whisper_model = whisper_model
        self.settings = None
        self.add_case_window = None
        self.grid(row=0,
                  column=0,
                  sticky="news",
                  pady=10,
                  padx=10)
        self.grid_columnconfigure(0,
                                  weight=1)
        self.rowconfigure(0,
                          weight=1)
        self.rowconfigure(1,
                          weight=1)
        self.rowconfigure(2,
                          weight=20)
        self.rowconfigure(3,
                          weight=5)
        self.language = language
        self.new_case_button = CTkButton(self,
                                         text=language["new_case_button"],
                                         anchor="center",
                                         border_width=2,
                                         border_color="gray10",
                                         command=self.new_case)
        self.new_case_button.grid(column=0,
                                  row=0)

        self.cases_frame = ScrollableFrameCases(master=self,
                                                db=self.db,
                                                root=self.root,
                                                language=self.language)
        self.app_language_label = CTkLabel(self,
                                           text=self.language["language"] + ":",
                                           text_color="gray10",
                                           wraplength=300)
        self.app_language_label.grid(row=3,
                                     column=0,
                                     sticky="w",
                                     padx=10)
        self.app_language_combo_box = CTkComboBox(master=self,
                                                  command=self.update_options)
        self.app_language_combo_box.grid(row=3,
                                         sticky="e",
                                         column=0,
                                         padx=10)
        self.app_languages_options()

    def app_languages_options(self):
        languages = os.listdir("gui/AppLang")
        temp = []
        for language in languages:
            language = language.split(".")
            temp.append(language[0])
        del languages
        with open("GUI/app_options.json", "r") as file:
            options = json.load(file)
        self.app_language_combo_box.configure(values=temp)
        self.app_language_combo_box.set(value=options["app_lang"])

    def new_case(self):
        if self.add_case_window is None or not self.add_case_window.winfo_exists():
            self.add_case_window = AddCaseWindow(master=self, language=self.language)
            self.add_case_window.after(100,
                                       self.add_case_window.lift)
        else:
            self.add_case_window.focus()

    def update_app_language(self, language):
        self.language = language
        self.new_case_button.configure(text=language["new_case_button"])
        self.cases_frame.update_app_language(language)

    def update_options(self, choice):
        with open("GUI/app_options.json", "r") as file:
            options = json.load(file)
            data = {
                "app_lang": choice,
                "operation_mode": options["operation_mode"],
                "whisper_model": options["whisper_model"]
            }
        data = json.dumps(data, indent=2)
        with open("GUI/app_options.json", "w") as file:
            file.write(data)
        self.master.update_app_language()
