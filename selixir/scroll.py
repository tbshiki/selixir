from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
import logging
from typing import Union, Optional

# Get the logger
logger = logging.getLogger("selixir")


def scroll_to_element_by_js(driver, element: WebElement, top_offset: int = 100) -> None:
    """
    Scrolls to the specified web element, ensuring it's positioned at a specified offset from the top.

    Args:
        driver: The WebDriver instance controlling the browser.
        element: The web element to scroll to.
        top_offset: The vertical offset from the top of the page to position the element at.
                    Defaults to 100 pixels.
    """
    y_position = element.location["y"]
    scroll_position = max(0, y_position - top_offset)  # Ensure the scroll position is not negative

    driver.execute_script(f"window.scrollTo(0, {scroll_position});")


def scroll_to_target(driver, target: Union[WebElement, str], top_offset: int = 100, time_sleep: float = 1, raise_on_failure: bool = False) -> None:
    """
    Scrolls the browser window to the specified target, which can be a web element or an XPath string.
    Optionally positions the target at a specified offset from the top and waits for a specified time.

    Args:
        driver: The WebDriver instance controlling the browser.
        target: The web element or the XPath string of the element to scroll to.
        top_offset: The vertical offset from the top of the page to position the target at. Defaults to 100 pixels.
        time_sleep: Optional; Time to wait after scrolling to the target. Defaults to 1 second.
        raise_on_failure: If True, exceptions will be raised when scrolling fails.

    Raises:
        ValueError: If the target is None or empty.
        Exception: If raise_on_failure is True and any error occurs.
    """

    if not target:
        raise ValueError("The 'target' must not be None or empty.")

    try:
        if isinstance(target, WebElement):
            element = target
        else:
            element = driver.find_element(By.XPATH, target)
    except NoSuchElementException as e:
        logger.warning(f"Element not found: {target}")
        if raise_on_failure:
            raise e
        return
    except Exception as e:
        logger.error(f"Unexpected error while locating element: {e}")
        if raise_on_failure:
            raise e
        return

    try:
        actions = ActionChains(driver)
        actions.move_to_element(element).perform()
        WebDriverWait(driver, time_sleep).until(lambda d: element.is_displayed())
    except TimeoutException as e:
        logger.warning(f"Timeout while waiting for element to be displayed: {e}")
        if raise_on_failure:
            raise e
    except Exception as e:
        logger.warning(f"ActionChains scroll failed: {e}. Falling back to JavaScript scrolling.")
        try:
            if isinstance(element, WebElement):
                scroll_to_element_by_js(driver, element, top_offset)
            else:
                logger.error("Cannot scroll to element: invalid element reference")
                if raise_on_failure:
                    raise Exception("Invalid element reference for scrolling.")
        except Exception as js_error:
            logger.error(f"JavaScript scrolling also failed: {js_error}")
            if raise_on_failure:
                raise js_error

