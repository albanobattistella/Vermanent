from gui.SearchResults import SearchResults


class GuiInterface:
    def __init__(self,
                 search_result: SearchResults):
        self._search_result = search_result

    def print_results_on_gui(self):
        self._search_result.clear_results()
        self._search_result.print_results()
