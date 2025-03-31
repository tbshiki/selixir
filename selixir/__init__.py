from .driver import open_new_tab, close_other_tabs, wait_with_buffer, driver_start, perform_control_click, switch_to_rightmost_tab, switch_to_new_tab, debug
from .file import get_latest_file_path, wait_for_new_file, wait_for_download_completion
from .screenshot import take_fullpage_screenshot, take_element_screenshot
from .scroll import scroll_to_element_by_js, scroll_to_target


__all__ = [
    "open_new_tab",  #driver
    "close_other_tabs",  #driver
    "wait_with_buffer",  # .driver
    "driver_start",  # .driver
    "perform_control_click",  # .driver
    "switch_to_rightmost_tab",  # .driver
    "switch_to_new_tab",  # .driver
    "debug",  # .driver
    "get_latest_file_path",  # .file
    "wait_for_new_file",  # .file
    "wait_for_download_completion",  # .file
    "take_fullpage_screenshot",  # .screenshot
    "take_element_screenshot",  # .screenshot
    "scroll_to_element_by_js",  # .scroll
    "scroll_to_target",  # .scroll
]
