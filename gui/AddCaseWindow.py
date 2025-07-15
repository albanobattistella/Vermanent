from customtkinter import CTkLabel, CTkEntry, CTkButton, CTkToplevel, CTkScrollableFrame, END, filedialog
from PIL import ImageTk
from tkinter import messagebox
import string


class EvidenceInsertion:
    def __init__(self,
                 master,
                 index):
        self.label = CTkLabel(master=master,
                              text=index,
                              text_color="#DDD5D0")
        self.label.grid(row=index,
                        column=0,
                        sticky="we",
                        padx=10,
                        pady=10)

        self.evidence_name_entry = CTkEntry(master=master)
        self.evidence_name_entry.grid(row=index,
                                      column=1,
                                      sticky="we",
                                      padx=10,
                                      pady=10)
        self.evidence_path_entry = CTkEntry(master=master, )
        self.evidence_path_entry.grid(row=index,
                                      column=2,
                                      sticky="we",
                                      padx=10,
                                      pady=10)
        self.evidence_path_entry.bind("<Button-1>",
                                      self.on_click)

    def on_click(self,
                 event):
        directory = filedialog.askdirectory()
        self.evidence_path_entry.delete(0,
                                        END)
        self.evidence_path_entry.insert(0,
                                        directory)


class AddCaseWindow(CTkToplevel):
    def __init__(self, language, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.language = language
        self.path_column_label = None
        self.name_column_label = None
        self.number_of_evidences = []
        photo = ImageTk.PhotoImage(file='Assets/App_icon.png')
        self.wm_iconbitmap()
        self.after(201, lambda: self.iconphoto(False, photo))
        self.title("Vermanent")
        self.grid_rowconfigure(0,
                               weight=1)
        self.grid_rowconfigure(1,
                               weight=1)
        self.grid_rowconfigure(2,
                               weight=1)
        self.grid_rowconfigure(3,
                               weight=30)
        self.grid_rowconfigure(4,
                               weight=1)
        self.grid_columnconfigure(0,
                                  weight=1)
        self.grid_columnconfigure(1,
                                  weight=1)
        self.grid_columnconfigure(2,
                                  weight=1)
        self.grid_columnconfigure(3,
                                  weight=1)
        self.screen_resolution = {
            "width": self.winfo_screenwidth(),
            "height": self.winfo_screenheight()
        }
        self.window_size = {
            "width": 500,
            "height": 500
        }
        self.minsize(self.window_size["width"],
                     self.window_size["height"])
        x = (self.screen_resolution["width"] / 2) - (self.window_size["width"] / 2)
        y = (self.screen_resolution["height"] / 2) - (self.window_size["height"] / 2)
        self.geometry(f'{self.window_size["width"]}x{self.window_size["height"]}+{x}+{y}')
        self.scrollable_evidences_insertion = None
        self.evidence_insertion = []
        self.insert_case_name_label = CTkLabel(self,
                                               text=self.language["case_name"],
                                               text_color="#619B8A")
        self.insert_case_name_label.grid(row=0,
                                         column=0,
                                         sticky="n",
                                         padx=10,
                                         pady=10)
        self.insert_case_name = CTkEntry(self)
        self.insert_case_name.grid(row=0,
                                   column=1,
                                   columnspan=3,
                                   sticky="nwe",
                                   padx=10,
                                   pady=10,
                                   )
        self.insert_crime_type_label = CTkLabel(self,
                                                text=self.language["crime_type"],
                                                text_color="#619B8A")
        self.insert_crime_type_label.grid(row=1,
                                          column=0,
                                          sticky="n",
                                          padx=10,
                                          pady=10)
        self.insert_crime_type = CTkEntry(self)
        self.insert_crime_type.grid(row=1,
                                    column=1,
                                    columnspan=3,
                                    sticky="nwe",
                                    padx=10,
                                    pady=10)
        self.insert_number_of_evidences_label = CTkLabel(self,
                                                         text=self.language["number_of_evidences"],
                                                         text_color="#619B8A")
        self.insert_number_of_evidences_label.grid(row=2,
                                                   column=0,
                                                   sticky="n",
                                                   padx=10,
                                                   pady=10)
        vcmd = (self.register(self.callback))

        self.insert_number_of_evidences = CTkEntry(self,
                                                   width=50,
                                                   validate='all',
                                                   validatecommand=(vcmd, '%P'))
        self.insert_number_of_evidences.grid(row=2,
                                             column=1,
                                             columnspan=3,
                                             sticky="nw",
                                             padx=10,
                                             pady=10)
        self.insert_number_of_evidences.bind('<KeyRelease>',
                                             self.add_evidences_insertion)

        self.confirm_button = CTkButton(self,
                                        text=self.language["confirm"],
                                        command=self.add_case)
        self.confirm_button.grid(row=4,
                                 column=0,
                                 columnspan=2,
                                 sticky="e",
                                 padx=10,
                                 pady=10)
        self.cancel_button = CTkButton(self,
                                       text=self.language["cancel"],
                                       fg_color="gray64",
                                       command=self.destroy)
        self.cancel_button.grid(row=4,
                                column=2,
                                columnspan=2,
                                sticky="w",
                                padx=10,
                                pady=10)

    def callback(self, p):
        if str.isdigit(p) or p == "":
            return True
        else:
            return False

    def add_evidences_insertion(self, event):
        chars_allowed = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        if (event.char in chars_allowed or
                event.keysym == "BackSpace"):
            n_evidences = self.insert_number_of_evidences.get()
            if n_evidences == "":
                index = 0
            else:
                index = int(n_evidences)
            if index > 12:
                index = 12
                self.insert_number_of_evidences.delete(0,
                                                       END)
                self.insert_number_of_evidences.insert(0,
                                                       "12")
            self.evidence_insertion.clear()
            self.scrollable_evidences_insertion = CTkScrollableFrame(self)
            self.scrollable_evidences_insertion.grid(row=3,
                                                     column=0,
                                                     columnspan=4,
                                                     sticky="news",
                                                     padx=10,
                                                     pady=10)
            self.scrollable_evidences_insertion.grid_columnconfigure(0,
                                                                     weight=1)
            self.scrollable_evidences_insertion.grid_columnconfigure(1,
                                                                     weight=15)
            self.scrollable_evidences_insertion.grid_columnconfigure(2,
                                                                     weight=15)
            self.name_column_label = CTkLabel(self.scrollable_evidences_insertion,
                                              text=self.language["evidence_name"],
                                              text_color="#619B8A")
            self.name_column_label.grid(row=0,
                                        column=1,
                                        sticky="news",
                                        padx=10,
                                        pady=10)
            self.path_column_label = CTkLabel(self.scrollable_evidences_insertion,
                                              text=self.language["evidence_path"],
                                              text_color="#619B8A")
            self.path_column_label.grid(row=0,
                                        column=2,
                                        sticky="news",
                                        padx=10,
                                        pady=10)

            for i in range(0, int(index)):
                self.scrollable_evidences_insertion.grid_rowconfigure(i + 1,
                                                                      weight=1)
                self.evidence_insertion.append(EvidenceInsertion(master=self.scrollable_evidences_insertion,
                                                                 index=i + 1))

    def add_case(self):
        chars_allowed = list(string.ascii_letters + string.digits + "_" + "-")
        case_name = self.insert_case_name.get()
        if case_name == "":
            messagebox.showwarning(title=self.language["empty_case_name_title"],
                                   message=self.language["empty_case_name_message"])
            self.focus()
        elif any(char not in chars_allowed for char in case_name):
            messagebox.showwarning(title=self.language["bad_case_name_title"],
                                   message=self.language["bad_case_name_message"])
            self.focus()
        else:
            evidences = []
            if not self.evidence_insertion:
                messagebox.showwarning(title=self.language["empty_evidence_warning_title"],
                                       message=self.language["empty_evidence_warning_message"])
                self.focus()
            else:
                for evidence in self.evidence_insertion:
                    evidence_name = evidence.evidence_name_entry.get()
                    evidence_path = evidence.evidence_path_entry.get()
                    if any(char not in chars_allowed for char in evidence_name):
                        messagebox.showwarning(title=self.language["bad_evidence_name_title"],
                                               message=self.language["empty_case_name_message"])
                        self.focus()
                        return
                    else:
                        evidences.append([evidence_name, evidence_path])
                if any(evidence[0] == "" for evidence in evidences):

                    self.focus()
                elif any(evidence[1] == "" for evidence in evidences):
                    messagebox.showwarning(title=self.language["empty_path_warning_title"],
                                           message=self.language["empty_path_warning_message"])
                    self.focus()
                else:
                    self.master.master.db.create_case(case_name, evidences)
                    self.master.cases_frame.add_case_button(case_name=case_name,
                                                            row_index=len(self.master.cases_frame.cases_button))
                    self.destroy()
