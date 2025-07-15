from abc import ABC
from gui.Observer.Subject_number_files import SubjectNumberFiles


class Observer(ABC):
    def update(self, subject: SubjectNumberFiles) -> None:
        pass


class ConcreteObserver(Observer):

    def __init__(self,
                 language):
        self.number_analyzed_files_label = None
        self.language = language

    def update(self, subject: SubjectNumberFiles) -> None:
        total_number_of_files = subject._size
        already_analyzed_number = subject._already_analyzed_number
        self.number_analyzed_files_label.configure(text=str(already_analyzed_number) +
                                                        "/" +
                                                        str(total_number_of_files)
                                                        +
                                                        " "
                                                        + self.language["analyzed_files"])

    def set_label(self,
                  label):
        self.number_analyzed_files_label = label

    def update_app_language(self,
                            language):
        self.language = language
