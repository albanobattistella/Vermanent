from PIL import Image
from customtkinter import CTk, set_default_color_theme, CTkLabel, CTkImage

set_default_color_theme("Assets/Themes/vermanent_theme.json")


class BeginningWindow(CTk):
    def __init__(self):
        super().__init__()

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        window_width = int(screen_width * 0.50)
        window_height = int(window_width * 9 / 16)

        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2

        self.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        self.overrideredirect(True)
        self.attributes('-topmost', True)

        gif_path = "Assets/VERMANENT.gif"
        gif = Image.open(gif_path)

        self.background_label = CTkLabel(self, text="")
        self.background_label.place(relwidth=1, relheight=1)

        self.frames = []
        try:
            while True:
                self.frames.append(gif.copy())
                gif.seek(len(self.frames))
        except EOFError:
            pass

        self.frame_index = 0
        self.update_gif()

    def update_gif(self):
        window_width = int(self.winfo_screenwidth() * 0.50)
        window_height = int(self.winfo_screenheight() * 9 / 16)

        new_frame = self.frames[self.frame_index]
        new_bg = CTkImage(light_image=new_frame,
                          size=(window_width, window_height))
        self.background_label.configure(image=new_bg)
        self.background_label.image = new_bg

        self.frame_index = (self.frame_index + 1) % len(self.frames)
        self.after(50, self.update_gif)

