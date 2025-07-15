import json
from tkinter import messagebox
import torch
import whisper
from gui.tab_options_case_selector import TabOptions
from gui.empty_view import EmptyView
from PIL import ImageTk
from customtkinter import CTk, set_default_color_theme
from db.DbInterface import DbInterface
from threading import Semaphore

set_default_color_theme("Assets/Themes/vermanent_theme.json")


class App(CTk):
    def __init__(self):
        super().__init__()
        self._set_appearance_mode("dark")
        self.semaphore = Semaphore(1)
        self.model = None
        with open("gui/app_options.json") as options:
            app_options = json.load(options)
        with open("gui/AppLang/" + app_options["app_lang"] + ".json") as default_lang:
            self.language = json.load(default_lang)
        self.evidence_datas = []
        if app_options["operation_mode"] == "GPU":
            if torch.cuda.is_available():
                model = whisper.load_model(app_options["whisper_model"], device="cuda")
                chunk_seconds = 30
                mode = "GPU"
            else:
                messagebox.showwarning(title=self.language["GPU_not_found_title"],
                                       message=self.language["GPU_not_found_title"])
                model = None
                chunk_seconds = 30
                mode = "CPU"
        else:
            model = None
            chunk_seconds = 30
            mode = "CPU"
        self.set_model({"model": model,
                        "chunk_seconds": chunk_seconds,
                        "mode": mode})
        self.menu_bar = None
        self.db = DbInterface()
        self.title("Vermanent")
        photo = ImageTk.PhotoImage(file='Assets/App_icon.png')
        self.wm_iconbitmap()
        self.working_evidences = []
        self.case_views = []
        self.searchers = []
        self.iconphoto(False, photo)

        self.grid_rowconfigure(0,
                               weight=1,
                               pad=10)
        self.grid_columnconfigure(0,
                                  weight=1)
        self.grid_columnconfigure(1,
                                  weight=40)

        self.screen_resolution = {
            "width": self.winfo_screenwidth(),
            "height": self.winfo_screenheight()
        }
        self.app_size = {
            "width": int(self.screen_resolution["width"] * 0.85),
            "height": int(self.screen_resolution["height"] * 0.85)
        }
        self.minsize(self.app_size["width"],
                     self.app_size["height"])
        x = (self.screen_resolution["width"] / 2) - (self.app_size["width"] / 2)
        y = (self.screen_resolution["height"] / 2) - (self.app_size["height"] / 2)
        self.geometry(f'{self.app_size["width"]}x{self.app_size["height"]}+{x}+{y}')
        self.cases = []
        self.current_state = EmptyView(master=self,
                                       language=self.language)
        self.tab_options = TabOptions(master=self,
                                      whisper_model=app_options["whisper_model"],
                                      language=self.language,
                                      root=self,
                                      db=self.db,
                                      fg_color="#DDD5D0",
                                      app_mode=app_options["operation_mode"])
        self.focus()

    def close_case(self):
        case = self.current_state
        self.case_views.remove(case)
        self.current_state.hide()
        self.current_state.destroy()
        self.current_state = EmptyView(self,
                                       language=self.language)
        del case

    def update_app_language(self):
        with open("GUI/app_options.json", "r") as file:
            app_options = json.load(file)
        with open("gui/AppLang/" + app_options["app_lang"] + ".json") as default_lang:
            self.language = json.load(default_lang)
        self.tab_options.update_app_language(self.language)
        self.current_state.update_app_language(self.language)

    def set_model(self, model):
        self.model = model
