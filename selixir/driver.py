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

# Configure the logger
logger = logging.getLogger("selixir")


# デバッグモードが有効ならストリームハンドラーも追加
def debug(enable=False):
    """
    Enable or disable debug mode for selixir.

    When debug mode is enabled, log messages will be output to the console.

    Args:
        enable (bool): True to enable debug mode, False to disable
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


def perform_control_click(driver, element):
    """
    Perform a Control+click (or Command+click on Mac) on an element to open a link in a new tab.

    Args:
        driver: WebDriver instance
        element: The element to click on

    Returns:
        bool: True if a new tab was opened, False otherwise
    """
    handles_before_click = len(driver.window_handles)

    driver.execute_script("arguments[0].scrollIntoView();", element)

    actions = ActionChains(driver)
    control_key = Keys.COMMAND if platform.system() == "Darwin" else Keys.CONTROL
    actions.key_down(control_key).click(element).key_up(control_key).perform()

    try:
        WebDriverWait(driver, 30).until(lambda d: len(d.window_handles) > handles_before_click)
        logger.debug(f"新しいタブが開かれました ({len(driver.window_handles)} 個のタブ)")
        return True
    except TimeoutException:
        logger.warning("新しいタブが30秒以内に開かれませんでした")
        return False


def switch_to_rightmost_tab(driver, element):
    """
    Control+click on a link and switch to the rightmost (newest) tab.

    Args:
        driver: WebDriver instance
        element: The element to click on

    Returns:
        bool: True if successful, False otherwise
    """
    if perform_control_click(driver, element):
        driver.switch_to.window(driver.window_handles[-1])
        logger.debug(f"最も右のタブ({driver.window_handles[-1]})に切り替えました")
        return True
    return False


def switch_to_new_tab(driver, element):
    """
    Control+click on a link and switch to the newly opened tab.
    This function identifies the new tab by comparing handle lists before and after clicking.

    Args:
        driver: WebDriver instance
        element: The element to click on

    Returns:
        bool: True if successful, False otherwise
    """
    handle_list_before = driver.window_handles
    if perform_control_click(driver, element):
        handle_list_after = driver.window_handles
        handle_list_new = list(set(handle_list_after) - set(handle_list_before))
        if handle_list_new:
            driver.switch_to.window(handle_list_new[0])
            return True
    return False


def open_new_tab(driver, url, time_sleep=1):
    """
    Open a new tab with the specified URL and switch to it.

    Args:
        driver: WebDriver instance
        url: URL to load in the new tab
        time_sleep: Time to wait for the tab to open (seconds)

    Returns:
        list: List of newly created window handles
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
    Close all tabs except the current one (or specified tab).

    Args:
        driver: WebDriver instance
        current_tab_handle: Handle of the tab to keep open (defaults to current tab)

    Returns:
        str: Handle of the tab that remained open
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
        logger.debug(f"ページロード後、追加で{wait_time:.2f}秒待機します")

        # Simply use sleep (more efficient than WebDriverWait for this purpose)
        time.sleep(wait_time)
    except TimeoutException:
        logger.warning(f"ページの読み込みが{base_wait}秒以内に完了しませんでした")
    except Exception as e:
        logger.error(f"待機中にエラーが発生しました: {e}")


def driver_start(url, heroku_mode=False, verbose=False):
    """
    Start a Chrome WebDriver and load the specified URL.

    Handles common setup options and provides fallback mechanisms if the standard
    WebDriver initialization fails.

    Args:
        url: URL to load
        heroku_mode: Whether to use settings optimized for Heroku environment
        verbose: Whether to output status messages to stdout

    Returns:
        Initialized WebDriver instance
    """

    if verbose:
        print("ChromeDriver起動開始")

    # Log the information to the logger as well
    logger.info("ChromeDriver起動開始")

    options = webdriver.ChromeOptions()
    if heroku_mode:
        if verbose:
            print("Starting ChromeDriver with Heroku environment settings.")
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
        if verbose:
            print("ChromeDriver起動(Selenium)")
        logger.info("ChromeDriver起動(Selenium)")
    except Exception as e:
        if verbose:
            print(f"ChromeDriver起動エラー: {e}")
        logger.error(f"ChromeDriver起動エラー: {e}")
        service = Service(executable_path=ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        if verbose:
            print("ChromeDriver起動(ChromeDriverManager)")
        logger.info("ChromeDriver起動(ChromeDriverManager)")

    driver.maximize_window()
    wait_with_buffer(driver, 3, 1)
    if verbose:
        print("ChromeDriver起動完了")
    logger.info("ChromeDriver起動完了")

    driver.get(url)
    wait_with_buffer(driver, 3, 1)

    return driver
