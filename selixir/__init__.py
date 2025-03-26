
from .driver import ClickControl, open_new_tab, close_other_tabs
from .file import get_latest_file_path, wait_for_new_file
from .scroll import scroll_to_element_by_js, scroll_to_target, scroll_to_xpath

__all__ = [
    "ClickControl",
    "open_new_tab",
    "close_other_tabs",
    "get_latest_file_path",
    "wait_for_new_file",
    "scroll_to_element_by_js",
    "scroll_to_target",
]
