from customtkinter import CTkFrame, CTkLabel


class EmptyView(CTkFrame):
    def __init__(self,
                 master,
                 language,
                 **kwargs):
        super().__init__(master,
                         **kwargs)
        self.grid(row=0,
                  column=1,
                  sticky="news",
                  pady=10,
                  padx=10)
        self.grid_rowconfigure(0,
                               weight=1)
        self.grid_columnconfigure(0,
                                  weight=1)
        self.label = CTkLabel(self,
                              text=language["no_case_selected"],
                              anchor="center")
        self.label.grid(row=0,
                        column=0)

    def update_app_language(self,
                            language):
        self.label.configure(text=language["no_case_selected"])
