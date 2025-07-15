import os
import subprocess
import sys
from tkinter import ttk, CENTER, messagebox, filedialog
from tkinter.font import Font
from PIL import Image, ImageTk
from utils import load_audio_from_virtual_path, genera_pdf_report, extract_single_file_from_virtual_path
from customtkinter import CTkButton, CTkToplevel, CTkLabel


class ExportButton(CTkButton):
    def __init__(self,
                 master,
                 tree,
                 evidence_path,
                 language,
                 case_name,
                 evidence,
                 db,
                 **kwargs):
        super().__init__(master,
                         **kwargs)
        self.evidence = evidence
        self.case_name = case_name
        self.db = db
        self.language = language
        self.evidence_path = evidence_path
        self.tree = tree
        self.grid(row=1,
                  column=2,
                  pady=2,
                  sticky="w")
        self.configure(command=self.on_button_click)

    def on_button_click(self):
        if messagebox.askyesno(title=self.language["confirm_export_title"],
                               message=self.language["confirm_export_message"]):
            directory = filedialog.askdirectory(title=self.language["select_directory_title"])

            if not directory:
                messagebox.showinfo(title=self.language["select_directory_title"],
                                    message=self.language["no_directory_selected"])
                return
            try:
                selected_items = self.tree.selection()
                if not selected_items:
                    selected_items = self.tree.get_children()
                    if not selected_items:
                        messagebox.showinfo(title=self.language["No_search_results_title"],
                                            message=self.language["No_search_results_message"])
                    else:
                        for item in selected_items:
                            extract_single_file_from_virtual_path(base_directory=self.evidence_path,
                                                                  virtual_path=self.tree.item(item, "values")[0],
                                                                  is_temp_dir=False,
                                                                  extraction_temp_dir=directory)

                        messagebox.showinfo(title=self.language["report_generated_title"],
                                            message=self.language["report_generated_message"] + directory)
            except Exception as e:
                messagebox.showerror(f"Unexpected {e=}, {type(e)=}")

    def update_evidence(self,
                        evidence_path):
        self.evidence_path = evidence_path

    def update_app_language(self, language):
        self.language = language
        self.configure(text=self.language["Play_selected_file"])


class ReportButton(CTkButton):
    def __init__(self,
                 master,
                 tree,
                 evidence_path,
                 language,
                 case_name,
                 evidence,
                 db,
                 **kwargs):
        super().__init__(master,
                         **kwargs)
        self.evidence = evidence
        self.case_name = case_name
        self.db = db
        self.language = language
        self.evidence_path = evidence_path
        self.tree = tree
        self.grid(row=1,
                  column=1,
                  pady=2,
                  sticky="w")
        self.configure(command=self.on_button_click)

    def on_button_click(self):
        if messagebox.askyesno(title=self.language["confirm_report_generation_title"],
                               message=self.language["confirm_report_generation_message"]):
            directory = filedialog.askdirectory(title=self.language["select_directory_title"])

            if not directory:
                messagebox.showinfo(title=self.language["select_directory_title"],
                                    message=self.language["no_directory_selected"])
            try:
                selected_items = self.tree.selection()
                values = []
                if not selected_items:
                    selected_items = self.tree.get_children()
                if not selected_items:
                    messagebox.showinfo(title=self.language["No_search_results_title"],
                                        message=self.language["No_search_results_message"])
                else:
                    for item in selected_items:
                        value = self.tree.item(item, "values")
                        values.append(value[0])
                    evidence_data, results = self.db.take_data_for_report(case_name=self.case_name,
                                                                          evidence=self.evidence,
                                                                          file_names=values)
                    report_name = "/" + self.case_name + "_" + self.evidence + "_report.pdf"
                    genera_pdf_report(evidence_dict=evidence_data,
                                      results=results,
                                      logo_path="Assets/App_icon.png",
                                      output_path=directory + report_name,
                                      language=self.language)
                    messagebox.showinfo(title=self.language["report_generated_title"],
                                        message=self.language["report_generated_message"] + directory + report_name)
            except Exception as e:
                messagebox.showerror("Errore", str(e))

    def update_evidence(self,
                        evidence_path):
        self.evidence_path = evidence_path

    def update_app_language(self, language):
        self.language = language
        self.configure(text=self.language["generate_report_button"])


class PlayButton(CTkButton):
    def __init__(self,
                 master,
                 tree,
                 evidence_path,
                 language,
                 **kwargs):
        super().__init__(master,
                         **kwargs)
        self.temp_dirs = []
        self.language = language
        self.evidence_path = evidence_path
        self.tree = tree
        self.grid(row=1,
                  column=0,
                  pady=2,
                  sticky="w")
        self.configure(command=self.on_button_click)

    def play_audio(self,
                   audio_path):
        try:
            if sys.platform.startswith('win'):
                subprocess.Popen(['start', '', audio_path], shell=True)
            elif sys.platform.startswith('darwin'):
                subprocess.Popen(['open', audio_path])
            else:
                subprocess.Popen(['xdg-open', audio_path])

        except Exception as e:
            messagebox.showerror(message=f"Unexpected {e=}, {type(e)=}")

    def on_button_click(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning(title=self.language["no_selection"],
                                   message=self.language["select_a_row"])
            return
        elif len(selected_item) > 1:
            messagebox.showwarning(title=self.language["too_many_selections_title"],
                                   message=self.language["too_many_selections_message"])
            return

        values = self.tree.item(selected_item, "values")
        virtual_path = values[0]
        try:
            audio_path, temp_dir = load_audio_from_virtual_path(virtual_path, self.evidence_path)
            self.temp_dirs.append(temp_dir)
            if not os.path.isfile(audio_path):
                raise FileNotFoundError

            self.play_audio(audio_path=audio_path)

        except Exception as e:
            messagebox.showerror(f"Unexpected {e=}, {type(e)=}")

    def update_evidence(self,
                        evidence_path):
        self.evidence_path = evidence_path

    def update_app_language(self, language):
        self.language = language
        self.configure(text=self.language["Play_selected_file"])


class Tooltip:
    def __init__(self, widget):
        self.widget = widget
        self.tip_window = None
        self.current_iid = None
        self.current_column = None
        self.after_id = None

    def show(self, text, x, y, iid, column):
        self.hide()
        self.current_iid = iid
        self.current_column = column
        self.tip_window = tw = CTkToplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = CTkLabel(tw, text=text, corner_radius=5, wraplength=300)
        label.cget("font").configure(size=16)
        label.pack(ipadx=5, ipady=5)
        self.widget.after(100, self.ensure_valid_position)

    def hide(self):
        if self.after_id:
            self.widget.after_cancel(self.after_id)
            self.after_id = None
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None
            self.current_iid = None
            self.current_column = None

    def ensure_valid_position(self):
        if self.tip_window:
            x, y = self.tip_window.winfo_x(), self.tip_window.winfo_y()
            if not (0 <= x <= self.widget.winfo_screenwidth() and 0 <= y <= self.widget.winfo_screenheight()):
                self.hide()


class TreeviewResults(ttk.Treeview):

    def __init__(self,
                 evidence_path,
                 language,
                 master,
                 evidence,
                 case_name,
                 db,
                 **kwargs):
        super().__init__(master,
                         **kwargs)
        self.case_name = case_name
        self.evidence = evidence
        self.db = db
        self.language = language
        self.font = Font(font='TkDefaultFont')
        self.evidence_path = evidence_path
        play_image = Image.open("Assets/Play_button.png")
        play_image = play_image.resize((20, 20), Image.Resampling.LANCZOS)
        self.play_icon = ImageTk.PhotoImage(play_image)
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                        font=("Roboto", 12),
                        borderwidth=0,
                        background="#212121",
                        fieldbackground="#212121",
                        foreground="#DDD5D0",
                        rowheight=40)

        style.configure("Treeview.Heading",
                        background="#444444",
                        foreground="#619B8A",
                        borderwidth=0,
                        font=("Roboto", 13))
        style.map("Treeview.Heading",
                  background=[],
                  foreground=[])
        self['columns'] = ["filename",
                           "text",
                           "language",
                           "similarity"]

        self.column("#0", width=60, anchor=CENTER)
        self.column("filename", width=210, anchor=CENTER)
        self.column("text", width=250, anchor=CENTER)
        self.column("language", width=40, anchor=CENTER)
        self.column("similarity", width=40, anchor=CENTER)

        self.heading("#0", text="", anchor=CENTER)
        self.heading("filename", text=self.language["filename"], anchor=CENTER)
        self.heading("text", text=self.language["text"], anchor=CENTER)
        self.heading("language", text=self.language["language"], anchor=CENTER)
        self.heading("similarity", text=self.language["similarity"], anchor=CENTER)

        self.play_button = PlayButton(master=self.master,
                                      evidence_path=evidence_path,
                                      language=language,
                                      text=self.language["Play_selected_file"],
                                      tree=self)
        self.report_button = ReportButton(master=self.master,
                                          evidence_path=evidence_path,
                                          language=language,
                                          text=self.language["generate_report_button"],
                                          tree=self,
                                          evidence=self.evidence,
                                          case_name=self.case_name,
                                          db=self.db)

        self.export_button = ExportButton(master=self.master,
                                          evidence_path=evidence_path,
                                          language=language,
                                          text=self.language["export_button"],
                                          tree=self,
                                          evidence=self.evidence,
                                          case_name=self.case_name,
                                          db=self.db)
        self.grid(row=0,
                  column=0,
                  columnspan=4,
                  sticky="nswe")

        self.tooltip = Tooltip(self)
        self.bind("<Motion>", self.on_motion)
        self.bind("<Leave>", lambda event: self.hide_tooltip())
        self.after_id = None

    def hide_tooltip(self):
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None
        self.tooltip.hide()

    def print_results(self,
                      results):
        self.delete_results()
        self.after(1, lambda: self.insert_result(results))

    def delete_results(self):
        for item in self.get_children():
            self.delete(item)

    def insert_result(self,
                      results):
        if len(results) > 0:
            result = results.pop(0)
            file_name = result["file_name"]
            file_text = result["text"]
            similarity = result["similarity"]
            file_language = result["language"]

            self.insert("",
                        "end",
                        values=(file_name, file_text, file_language, similarity),
                        image=self.play_icon)
            self.after(1, lambda: self.insert_result(results))

    def update_evidence(self, evidence_path):
        self.evidence_path = evidence_path
        self.play_button.update_evidence(evidence_path=evidence_path)

    def update_app_language(self,
                            language):
        self.language = language
        self.heading("filename", text=self.language["filename"], anchor=CENTER)
        self.heading("text", text=self.language["text"], anchor=CENTER)
        self.heading("language", text=self.language["language"], anchor=CENTER)
        self.heading("similarity", text=self.language["similarity"], anchor=CENTER)
        self.play_button.update_app_language(language)
        self.report_button.update_app_language(language)
        self.export_button.update_app_language(language)

    def on_motion(self, event):
        region = self.identify("region", event.x, event.y)
        if region != "cell":
            self.hide_tooltip()
            return
        iid = self.identify_row(event.y)
        column = self.identify_column(event.x)
        if not iid or not column:
            self.tooltip.hide()
            return
        if iid != self.tooltip.current_iid or column != self.tooltip.current_column:
            self.hide_tooltip()
        col_index = int(column.replace("#", "")) - 1
        if col_index != 1:
            self.tooltip.hide()
            return

        cell_values = self.item(iid, "values")
        text = cell_values[col_index] if col_index < len(cell_values) else ""
        if not text:
            self.hide_tooltip()
            return

        x = self.winfo_rootx() + event.x + 20
        y = self.winfo_rooty() + event.y + 20

        if self.after_id:
            self.after_cancel(self.after_id)

        self.after_id = self.after(300, lambda: self.tooltip.show(text, x, y, iid, column))
