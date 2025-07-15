import json
from customtkinter import CTk, set_default_color_theme, CTkButton, CTkComboBox, CTkLabel


set_default_color_theme("Assets/Themes/vermanent_theme.json")


class ModelWindow(CTk):
    def __init__(self):
        super().__init__()

        with open("gui/app_options.json") as options:
            app_options = json.load(options)
        with open("gui/AppLang/" + app_options["app_lang"] + ".json") as default_lang:
            self.language = json.load(default_lang)
        self.app_lang = app_options["app_lang"]
        self.app_mode = app_options["operation_mode"]
        self.whisper_model = app_options["whisper_model"]

        self.grid_rowconfigure(0,
                               weight=5,
                               )
        self.grid_rowconfigure(1,
                               weight=5,
                               )
        self.grid_rowconfigure(2,
                               weight=1,
                               )
        self.grid_columnconfigure(0,
                                  weight=1)
        self.grid_columnconfigure(1,
                                  weight=40)

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        window_width = int(screen_width * 0.30)
        window_height = int(window_width * 9 / 16)

        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2

        self.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        self.overrideredirect(True)
        self.attributes('-topmost', True)

        self.whisper_model_label = CTkLabel(self,
                                            text=self.language["select_whisper_model"],
                                            text_color="#619B8A",
                                            wraplength=300)
        self.whisper_model_label.grid(row=0,
                                      column=0,
                                      sticky="w",
                                      padx=10,
                                      pady=10)

        self.whisper_model_combo_box = CTkComboBox(master=self)
        self.whisper_model_combo_box.grid(row=0,
                                          column=1,
                                          sticky="w")
        self.app_mode_label = CTkLabel(self,
                                       text=self.language["select_app_mode"],
                                       text_color="#619B8A",
                                       wraplength=300)
        self.app_mode_label.grid(row=1,
                                 column=0,
                                 sticky="w",
                                 padx=10,
                                 pady=10)
        self.app_mode_combo_box = CTkComboBox(master=self)
        self.app_mode_combo_box.grid(row=1,
                                     column=1,
                                     sticky="w")

        self.whisper_model_options()

        self.confirm_button = CTkButton(self,
                                        text=self.language["confirm"],
                                        command=self.update_options)
        self.confirm_button.grid(row=2,
                                 column=0,
                                 columnspan=2,
                                 padx=10,
                                 pady=10)

    def whisper_model_options(self):
        temp = ["tiny", "base", "small", "medium", "large", "turbo"]

        self.whisper_model_combo_box.configure(values=temp)
        self.whisper_model_combo_box.set(value=self.whisper_model)
        temp = ["GPU", "CPU"]
        self.app_mode_combo_box.configure(values=temp)
        self.app_mode_combo_box.set(value=self.app_mode)

    def update_options(self):
        whisper_model = self.whisper_model_combo_box.get()
        app_mode = self.app_mode_combo_box.get()
        data = {
            "app_lang": self.app_lang,
            "operation_mode": app_mode,
            "whisper_model": whisper_model
        }
        data = json.dumps(data, indent=2)
        with open("GUI/app_options.json", "w") as file:
            file.write(data)
        self.destroy()
