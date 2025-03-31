from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
import logging

logger = logging.getLogger("selixir")

def take_fullpage_screenshot(driver: webdriver.Chrome, filename: str) -> str:
    """
    Take a full page screenshot, including content below the fold.

    Args:
        driver: WebDriver instance
        filename: Path to save the screenshot

    Returns:
        Path to the saved screenshot
    """
    try:
        # Get the total height of the page
        total_height = driver.execute_script("return document.body.scrollHeight")
        total_width = driver.execute_script("return document.body.scrollWidth")

        # Set window size to capture everything
        original_size = driver.get_window_size()
        driver.set_window_size(total_width, total_height)

        # Take screenshot
        driver.save_screenshot(filename)
    finally:
        # Restore original window size
        driver.set_window_size(original_size['width'], original_size['height'])

    return filename


def take_element_screenshot(driver: webdriver.Chrome, element: WebElement, filename: str) -> str:
    """
    Take a screenshot of a specific element.

    Args:
        driver: WebDriver instance
        element: WebElement to capture
        filename: Path to save the screenshot

    Returns:
        Path to the saved screenshot
    """
    # Scroll element into view
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    WebDriverWait(driver, 5).until(lambda d: element.is_displayed())

    # Save the screenshot
    element.screenshot(filename)

    logger.info(f"Saved element screenshot to {filename}")

    return filename
