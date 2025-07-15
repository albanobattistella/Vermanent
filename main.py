import multiprocessing
import gui.app
from gui.BeginningWindow import BeginningWindow
from utils import check_dependencies
from gui.model_selector_window import ModelWindow
import time
from utils import cleanup_temp_dir
import os


def run_ctk_app():
    initial_view = BeginningWindow()
    initial_view.mainloop()


def create_directory_if_not_exists(new_dir):
    project_path = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(project_path, new_dir)
    os.makedirs(full_path, exist_ok=True)


def run_model_settings():
    model_window = ModelWindow()
    model_window.mainloop()


if __name__ == '__main__':
    create_directory_if_not_exists("db/cases")
    create_directory_if_not_exists("search/search_models")
    if check_dependencies():
        multiprocessing.freeze_support()
        model_settings_process = multiprocessing.Process(target=run_model_settings)
        model_settings_process.start()
        model_settings_process.join()
        cleanup_temp_dir()
        process = multiprocessing.Process(target=run_ctk_app)
        process.start()
        start = time.time()
        app = gui.app.App()
        end = time.time()
        loading_time = end - start
        if loading_time < 20:
            time.sleep(20 - loading_time)
        process.terminate()
        app.mainloop()
