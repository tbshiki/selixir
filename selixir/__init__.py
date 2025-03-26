from .driver import open_new_tab, close_other_tabs, wait_with_buffer, driver_start, perform_control_click, switch_to_rightmost_tab, switch_to_new_tab, debug
from .file import get_latest_file_path, wait_for_new_file
from .scroll import scroll_to_element_by_js, scroll_to_target

__all__ = [
    "open_new_tab",
    "close_other_tabs",
    "wait_with_buffer",
    "driver_start",
    "perform_control_click",
    "switch_to_rightmost_tab",
    "switch_to_new_tab",
    "debug",
    "get_latest_file_path",
    "wait_for_new_file",
    "scroll_to_element_by_js",
    "scroll_to_target",
]
