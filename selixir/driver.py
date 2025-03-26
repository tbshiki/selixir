from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

import random
import time
import platform
import logging

logger = logging.getLogger(__name__)


class ClickControl:
    """
    Control-click action on a web element, handling new tabs and window switches.
    """

    def __init__(self, driver, element):
        """
        Initializes the ClickControl instance.
        Args:
            driver: WebDriver instance.
            element: The web element to be clicked.
        """
        self._perform_click(driver, element)

    def _perform_click(self, driver, element):
        """
        Perform a control-click on the specified element and wait for a new tab to open.

        This method scrolls the element into view, performs a control-click (Command-click on macOS,
        Control-click on other systems), and waits for a new browser tab to open.

        Args:
            driver: The WebDriver instance controlling the browser.
            element: The web element to be clicked.

        Raises:
            TimeoutException: If no new tab is opened within 30 seconds.
        """

        handles_before_click = len(driver.window_handles)  # Get the number of handles before the click

        driver.execute_script("arguments[0].scrollIntoView();", element)  # Scroll the element into view to avoid errors

        # Setup action chains for the click
        actions = ActionChains(driver)
        control_key = Keys.COMMAND if platform.system() == "Darwin" else Keys.CONTROL
        actions.key_down(control_key).click(element).key_up(control_key).perform()

        # Wait for a new tab to open (up to 30 seconds)
        try:
            WebDriverWait(driver, 30).until(lambda d: len(d.window_handles) > handles_before_click)
        except TimeoutException:
            print("Timeout occurred: No new tab was opened.")
            return

    @staticmethod
    def switch_to_rightmost(driver, element):
        """
        Control-clicks on the given element and switches to the rightmost tab.
        Args:
            driver: WebDriver instance.
            element: The web element to be clicked.
        """
        ClickControl(driver, element)
        driver.switch_to.window(driver.window_handles[-1])

    @staticmethod
    def switch_to_new_tab(driver, element):
        """
        Control-clicks on the given element and switches to the newly opened tab.
        Args:
            driver: WebDriver instance.
            element: The web element to be clicked.
        """
        handle_list_before = driver.window_handles
        ClickControl(driver, element)

        handle_list_after = driver.window_handles
        handle_list_new = list(set(handle_list_after) - set(handle_list_before))
        driver.switch_to.window(handle_list_new[0])


def open_new_tab(driver, url, time_sleep=1):
    """
    Opens a new tab with the specified URL and switches the driver's context to this new tab.

    Args:
        driver: The WebDriver instance controlling the browser.
        url: The URL to be opened in the new tab.
        time_sleep: Optional; The time to wait for the new tab to open.

    Returns:
        A list of new window handle(s) created.
    """
    handles_before = driver.window_handles
    driver.execute_script(f"window.open('{url}');")

    # Wait for the new tab to open
    WebDriverWait(driver, time_sleep).until(lambda d: len(d.window_handles) > len(handles_before))

    handles_after = driver.window_handles
    new_handles = list(set(handles_after) - set(handles_before))
    driver.switch_to.window(new_handles[0])

    return new_handles


def close_other_tabs(driver, current_tab_handle=None):
    """
    Closes all browser tabs except for the current tab and switches back to the current tab.

    Args:
        driver: The WebDriver instance controlling the browser.
        current_tab_handle: The handle of the current tab that should remain open.
    """
    if current_tab_handle is None:
        current_tab_handle = driver.current_window_handle

    for handle in driver.window_handles:
        if handle != current_tab_handle:
            driver.switch_to.window(handle)
            driver.close()

    driver.switch_to.window(current_tab_handle)

    return current_tab_handle


def wait_with_buffer(driver, time_sleep=1, buffer_time=0.5, base_wait=10):
    """
    Wait for the page to load completely and then wait for a specified time with random buffer.

    Args:
        driver: The WebDriver instance controlling the browser.
        time_sleep: The minimum time to wait after page load.
        buffer_time: Additional random time to add (up to this value).
        base_wait: Maximum time to wait for page to reach 'complete' state.
    """
    WebDriverWait(driver, base_wait).until(lambda d: d.execute_script("return document.readyState") == "complete")
    wait_time = random.uniform(time_sleep, time_sleep + buffer_time)
    start = time.time()
    WebDriverWait(driver, wait_time).until(lambda d: time.time() - start > wait_time)


def driver_start(url, heroku_mode=False, logger=None):
    """
    Start a Chrome WebDriver instance with specified options.

    Args:
        url: The URL to navigate to after starting the driver.
        heroku_mode: Whether to configure the driver for a Heroku environment.
        logger: Optional logger instance for logging information.

    Returns:
        The initialized WebDriver instance.
    """
    if logger:
        logger.info("ChromeDriver起動開始")

    options = webdriver.ChromeOptions()
    if heroku_mode == "True":
        if logger:
            logger.info("Heroku環境の設定でChromeDriverを起動します。")
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
        if logger:
            logger.info("ChromeDriver起動(Selenium)")
    except Exception as e:
        if logger:
            logger.error(f"ChromeDriver起動1エラー: {e}")
        service = Service(executable_path=ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        if logger:
            logger.info("ChromeDriver起動(ChromeDriverManager)")

    driver.maximize_window()
    wait_with_buffer(driver, 3, 1)
    if logger:
        logger.info("ChromeDriver起動完了")

    driver.get(url)
    wait_with_buffer(driver, 3, 1)

    return driver
