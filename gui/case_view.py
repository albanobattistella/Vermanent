import string
from tkinter import messagebox
from PIL import Image
from customtkinter import CTkFrame, CTkLabel, CTkComboBox, CTkButton, CTkEntry, END, filedialog, CTkImage
from gui.evidence_view import EvidenceView


class CaseView(CTkFrame):
    def __init__(self,
                 master,
                 language,
                 db,
                 case_name,
                 evidences,

                 **kwargs):
        super().__init__(master,
                         **kwargs)
        self.close_case_button = None
        self.close_case_label = None
        self.add_evidence_button = None
        self.add_evidence_path_entry = None
        self.add_evidence_path_label = None
        self.add_evidence_entry = None
        self.add_evidence_label = None
        self.bin_button = None
        self.evidences_switch = None
        self.case_name_label = None
        self.current_evidence_view = None
        self.db = db
        self.language = language
        self.case_name = case_name
        self.evidences = evidences
        self.evidences_view = []

        self.grid_rowconfigure(0,
                               weight=1)
        self.grid_rowconfigure(1,
                               weight=1)
        self.grid_rowconfigure(2,
                               weight=1)
        self.grid_rowconfigure(3,
                               weight=1)
        self.grid_rowconfigure(4,
                               weight=1)
        self.grid_rowconfigure(5,
                               weight=3)
        self.grid_rowconfigure(6,
                               weight=1)
        self.grid_rowconfigure(7,
                               weight=80)
        self.grid_columnconfigure(0,
                                  weight=1)
        self.grid_columnconfigure(1,
                                  weight=15)
        self.grid_columnconfigure(2,
                                  weight=15)
        self.grid_columnconfigure(3,
                                  weight=15)
        self.grid_columnconfigure(4,
                                  weight=15)
        self.grid_columnconfigure(5,
                                  weight=30)
        self.grid_columnconfigure(6,
                                  weight=30)

        self.create_widgets()
        for evidence_data in self.evidences:
            self.evidences_view.append(EvidenceView(master=self,
                                                    root=self.master,
                                                    language=self.language,
                                                    evidence_data=evidence_data,
                                                    case_name=self.case_name,
                                                    db=self.db))

    def create_widgets(self):
        self.case_name_label = CTkLabel(self,
                                        text=self.case_name,
                                        font=("roboto", 30),
                                        text_color="#DDD5D0")

        values = []
        for evidence_data in self.evidences:
            values.append(evidence_data["evidence"])
        self.evidences_switch = CTkComboBox(self,
                                            values=values,
                                            command=self.switch_evidence)
        self.bin_button = CTkButton(self,
                                    image=CTkImage(light_image=Image.open('Assets/recycle_bin.png'),
                                                   dark_image=Image.open('Assets/recycle_bin.png'),
                                                   size=(20, 20)),
                                    text="",
                                    width=25,
                                    height=20,
                                    fg_color="#ff3131",
                                    hover_color="#841818",
                                    command=self.delete_evidence)

        self.add_evidence_label = CTkLabel(self,
                                           text=self.language["evidence_name"],
                                           text_color="#619B8A")

        self.add_evidence_entry = CTkEntry(self)

        self.add_evidence_path_label = CTkLabel(self,
                                                text=self.language["evidence_path"],
                                                text_color="#619B8A")

        self.add_evidence_path_entry = CTkEntry(self)

        self.add_evidence_path_entry.bind("<Button-1>",
                                          self.ask_directory)
        self.add_evidence_button = CTkButton(self,
                                             text=self.language["add_evidence"],
                                             command=self.add_evidence)
        self.close_case_label = CTkLabel(self,
                                         text=self.language["close_case"],
                                         text_color="#ff3131")
        self.close_case_button = CTkButton(self,
                                           text="X",
                                           font=("roboto", 20, "bold"),
                                           width=25,
                                           height=20,
                                           fg_color="#ff3131",
                                           hover_color="#841818",
                                           command=self.close_case)

    def close_case(self):
        for evidence in self.evidences_view:
            if evidence.evidence_data.state in ["creating", "transcribing", "finalizing"] \
                    or evidence.evidence_data.search_state == "searching":
                messagebox.showwarning(title=self.language["running_operation_warning_title"],
                                       message=self.language["running_operation_warning_message"])
                return
        self.master.close_case()

    def display(self):
        self.grid(row=0,
                  column=1,
                  sticky="news",
                  pady=10,
                  padx=10)
        self.close_case_button.grid(row=0,
                                    column=6,
                                    sticky="e",
                                    pady=10,
                                    padx=10)
        self.close_case_label.grid(row=0,
                                   column=6,
                                   sticky="we",
                                   pady=10,
                                   padx=10)
        self.case_name_label.grid(row=0,
                                  column=0,
                                  columnspan=5,
                                  sticky="w",
                                  pady=10,
                                  padx=10)
        self.evidences_switch.grid(row=2,
                                   column=0,
                                   sticky="w",
                                   padx=10,
                                   pady=5)
        self.bin_button.grid(row=2,
                             column=1,
                             sticky="w",
                             padx=10,
                             pady=5)
        self.add_evidence_label.grid(row=1,
                                     column=2,
                                     sticky="sw",
                                     padx=5)
        self.add_evidence_entry.grid(row=2,
                                     column=2,
                                     sticky="ew",
                                     padx=5)
        self.add_evidence_path_label.grid(row=1,
                                          column=3,
                                          sticky="sw",
                                          padx=5)
        self.add_evidence_path_entry.grid(row=2,
                                          column=3,
                                          sticky="ew",
                                          padx=5)
        self.add_evidence_button.grid(row=2,
                                      column=4,
                                      sticky="w",
                                      padx=5)
        for evidence_view in self.evidences_view:
            if self.evidences_switch.get() == evidence_view.evidence_data.evidence:
                self.current_evidence_view = evidence_view
                self.current_evidence_view.display()

    def hide(self):
        self.grid_forget()
        self.bin_button.grid_forget()
        self.close_case_label.grid_forget()
        self.close_case_button.grid_forget()
        self.case_name_label.grid_forget()
        self.evidences_switch.grid_forget()
        self.add_evidence_label.grid_forget()
        self.add_evidence_entry.grid_forget()
        self.add_evidence_path_label.grid_forget()
        self.add_evidence_path_entry.grid_forget()
        self.add_evidence_button.grid_forget()
        self.current_evidence_view.hide()

    def ask_directory(self,
                      event):
        directory = filedialog.askdirectory()
        self.add_evidence_path_entry.delete(0,
                                            END)
        self.add_evidence_path_entry.insert(0,
                                            directory)

    def add_evidence(self):
        chars_allowed = list(string.ascii_letters + string.digits + "_" + "-")
        evidence_name = self.add_evidence_entry.get()
        evidence_path = self.add_evidence_path_entry.get()
        self.add_evidence_entry.delete(0,
                                       END)
        self.add_evidence_path_entry.delete(0,
                                            END)
        if any(char not in chars_allowed for char in evidence_name):
            messagebox.showwarning(title=self.language["bad_evidence_name_title"],
                                   message=self.language["bad_evidence_name_message"])
        elif "" == evidence_name:
            messagebox.showwarning(title=self.language["empty_evidence_warning_title"],
                                   message=self.language["empty_evidence_warning_message"])
        elif "" == evidence_path:
            messagebox.showwarning(title=self.language["empty_path_warning_title"],
                                   message=self.language["empty_path_warning_message"])
        else:
            self.db.insert_evidence(case_name=self.case_name,
                                    evidence=evidence_name,
                                    path=evidence_path)
            current_evidences = self.evidences_switch.cget("values")
            current_evidences.append(evidence_name)
            evidence_data = {
                "evidence": evidence_name,
                "files_path": evidence_path,
                "transcriptions": "creating"
            }
            self.evidences.append(evidence_data)
            self.evidences_view.append(EvidenceView(master=self,
                                                    root=self.master,
                                                    language=self.language,
                                                    evidence_data=evidence_data,
                                                    case_name=self.case_name,
                                                    db=self.db))
            self.evidences_switch.configure(values=current_evidences)

    def switch_evidence(self, choice):
        self.current_evidence_view.hide()
        for evidence_view in self.evidences_view:
            if choice == evidence_view.evidence_data.evidence:
                self.current_evidence_view = evidence_view
                self.current_evidence_view.display()

    def update_app_language(self,
                            language):
        self.language = language
        self.add_evidence_label.configure(text=language["evidence_name"])
        self.add_evidence_path_label.configure(text=language["evidence_path"])
        self.add_evidence_button.configure(text=language["add_evidence"])
        self.close_case_label.configure(text=language["close_case"])
        for evidence_view in self.evidences_view:
            evidence_view.update_app_language(language)

    def delete_evidence(self):
        answer_yes = messagebox.askokcancel(title="",
                                            message=self.language["ask_confirm_evidence"])
        if answer_yes:
            if (self.current_evidence_view.evidence_data.state not in ["creating", "transcribing", "finalizing"]
                    and self.current_evidence_view.evidence_data.search_state != "searching"):
                self.current_evidence_view.hide()
                evidence = self.evidences_switch.get()
                self.db.delete_evidence(case_name=self.case_name,
                                        evidence=evidence)
                for evidence_view in self.evidences_view:
                    if evidence_view.evidence_data.evidence == evidence:
                        self.evidences_view.remove(evidence_view)
                switch_values = self.evidences_switch.cget("values")
                for value in switch_values:
                    if value == evidence:
                        switch_values.remove(value)
                self.evidences_switch.configure(values=switch_values)
                self.evidences_switch.set(switch_values[0])
                choice = switch_values[0]
                for evidence_view in self.evidences_view:
                    if choice == evidence_view.evidence_data.evidence:
                        self.current_evidence_view = evidence_view
                        self.current_evidence_view.display()
            else:
                messagebox.showerror(title=self.language["deleting_evidence_error"],
                                     message=self.language["fail_eliminate_evidence"])
