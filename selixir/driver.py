from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager

import random
import time
import platform
import logging
from typing import List, Optional, Union, Literal, Any, Callable, TypeVar, cast

# Configure the logger
logger = logging.getLogger("selixir")

# Type variable for WebDriver
Driver = TypeVar('Driver', bound='webdriver.Chrome')


def debug(enable: bool = False) -> None:
    """
    Enable or disable debug mode for selixir.

    When debug mode is enabled, log messages will be output to the console.

    Args:
        enable: True to enable debug mode, False to disable
    """
    if enable:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.WARNING)
        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.NullHandler):
                logger.removeHandler(handler)


def perform_control_click(driver: webdriver.Chrome, element: WebElement) -> bool:
    """
    Perform a Control+click (or Command+click on Mac) on an element to open a link in a new tab.

    Args:
        driver: WebDriver instance
        element: The element to click on

    Returns:
        True if a new tab was opened, False otherwise
    """
    handles_before_click = len(driver.window_handles)

    driver.execute_script("arguments[0].scrollIntoView();", element)

    actions = ActionChains(driver)
    control_key = Keys.COMMAND if platform.system() == "Darwin" else Keys.CONTROL
    actions.key_down(control_key).click(element).key_up(control_key).perform()

    try:
        WebDriverWait(driver, 30).until(lambda d: len(d.window_handles) > handles_before_click)
        logger.debug(f"New tab opened ({len(driver.window_handles)} tabs total)")
        return True
    except TimeoutException:
        logger.warning("New tab was not opened within 30 seconds")
        return False


def switch_to_rightmost_tab(driver: webdriver.Chrome, element: WebElement) -> bool:
    """
    Control+click on a link and switch to the rightmost (newest) tab.

    Args:
        driver: WebDriver instance
        element: The element to click on

    Returns:
        True if successful, False otherwise
    """
    if perform_control_click(driver, element):
        driver.switch_to.window(driver.window_handles[-1])
        logger.debug(f"Switched to the rightmost tab ({driver.window_handles[-1]})")
        return True
    return False


def switch_to_new_tab(driver: webdriver.Chrome, element: WebElement) -> bool:
    """
    Control+click on a link and switch to the newly opened tab.
    This function identifies the new tab by comparing handle lists before and after clicking.

    Args:
        driver: WebDriver instance
        element: The element to click on

    Returns:
        True if successful, False otherwise
    """
    handle_list_before = driver.window_handles
    if perform_control_click(driver, element):
        handle_list_after = driver.window_handles
        handle_list_new = list(set(handle_list_after) - set(handle_list_before))
        if handle_list_new:
            driver.switch_to.window(handle_list_new[0])
            return True
    return False


def open_new_tab(driver: webdriver.Chrome, url: str, timeout: float = 10) -> List[str]:
    """
    Open a new tab with the specified URL and switch to it.

    Args:
        driver: WebDriver instance
        url: URL to load in the new tab
        timeout: Maximum time to wait for the new tab to open (seconds)

    Returns:
        List of newly created window handles
    """
    handles_before = driver.window_handles
    driver.execute_script(f"window.open('{url}');")

    try:
        # Wait for the new tab to open with proper WebDriverWait usage
        # This waits up to 'timeout' seconds for the condition to be true
        WebDriverWait(driver, timeout).until(lambda d: len(d.window_handles) > len(handles_before))

        handles_after = driver.window_handles
        new_handles = list(set(handles_after) - set(handles_before))

        if new_handles:
            driver.switch_to.window(new_handles[0])
            logger.debug(f"Switched to new tab with handle {new_handles[0]}")
            return new_handles
        else:
            logger.warning("No new tab was detected after script execution")
            return []

    except TimeoutException:
        logger.warning(f"Timed out waiting for new tab to open (timeout: {timeout}s)")
        return []


def close_other_tabs(driver: webdriver.Chrome, current_tab_handle: Optional[str] = None) -> str:
    """
    Close all tabs except the current one (or specified tab).

    Args:
        driver: WebDriver instance
        current_tab_handle: Handle of the tab to keep open (defaults to current tab)

    Returns:
        Handle of the tab that remained open
    """
    if current_tab_handle is None:
        current_tab_handle = driver.current_window_handle

    for handle in driver.window_handles:
        if handle != current_tab_handle:
            driver.switch_to.window(handle)
            driver.close()

    driver.switch_to.window(current_tab_handle)

    return current_tab_handle


def wait_with_buffer(driver: webdriver.Chrome, time_sleep: float = 1, buffer_time: float = 0.5, base_wait: int = 10) -> None:
    """
    Wait for the page to finish loading, then add a random buffer wait time.
    This helps prevent detection of automated browsing patterns by adding variability.

    Args:
        driver: WebDriver instance
        time_sleep: Minimum wait time (seconds)
        buffer_time: Maximum additional random wait time (seconds)
        base_wait: Maximum time to wait for page loading completion (seconds)
    """
    try:
        # Wait for the page to be fully loaded
        WebDriverWait(driver, base_wait).until(lambda d: d.execute_script("return document.readyState") == "complete")

        # Calculate random additional wait time
        wait_time = random.uniform(time_sleep, time_sleep + buffer_time)
        logger.debug(f"Waiting for additional {wait_time:.2f} seconds after page load")

        # Simply use sleep (more efficient than WebDriverWait for this purpose)
        time.sleep(wait_time)
    except TimeoutException:
        logger.warning(f"Page did not finish loading within {base_wait} seconds")
    except Exception as e:
        logger.error(f"Error during wait: {e}")


def driver_start(url: str, heroku_mode: Union[bool, str] = False) -> webdriver.Chrome:
    """
    Start a Chrome WebDriver and load the specified URL.

    Handles common setup options and provides fallback mechanisms if the standard
    WebDriver initialization fails.

    To see detailed logs, enable debug mode by calling selixir.debug(True) before using this function.

    Args:
        url: URL to load
        heroku_mode: Whether to use settings optimized for Heroku environment

    Returns:
        Initialized WebDriver instance
    """

    logger.info("Starting ChromeDriver")

    options = webdriver.ChromeOptions()
    # Handle both boolean True and string 'True'/'true'
    is_heroku_mode = heroku_mode is True or (isinstance(heroku_mode, str) and heroku_mode.lower() == "true")

    if is_heroku_mode:
        logger.info("Starting ChromeDriver with Heroku environment settings.")
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-setuid-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--disable-background-networking")
        options.add_argument("--disable-hang-monitor")
        options.add_argument("--disable-sync")
        options.add_argument("--disable-default-apps")
        options.add_argument("--mute-audio")
        options.add_argument("--metrics-recording-only")
        options.add_argument("--no-first-run")
        options.add_argument("--disable-site-isolation-trials")

    options.add_argument("--start-maximized")
    options.add_argument("--lang=ja-JP")

    prefs = {
        "profile.default_content_setting_values.popups": 2,
        "profile.default_content_setting_values.geolocation": 2,
        "profile.default_content_setting_values.notifications": 2,
        "disk-cache-size": 10485760,
        "safebrowsing.enabled": True,
    }
    options.add_experimental_option("prefs", prefs)

    try:
        driver = webdriver.Chrome(options=options)
        logger.info("ChromeDriver started (Selenium)")
    except Exception as e:
        logger.error(f"ChromeDriver start error: {e}")
        service = Service(executable_path=ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        logger.info("ChromeDriver started (ChromeDriverManager)")

    driver.maximize_window()
    wait_with_buffer(driver, 3, 1)
    logger.info("ChromeDriver initialization complete")

    driver.get(url)
    wait_with_buffer(driver, 3, 1)

    return driver
