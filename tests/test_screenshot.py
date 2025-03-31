import pytest
from unittest.mock import MagicMock, patch
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selixir.screenshot import take_fullpage_screenshot, take_element_screenshot

@pytest.fixture
def mock_driver():
    """ChromeDriverのモックを作成するフィクスチャ"""
    driver = MagicMock(spec=webdriver.Chrome)
    # window_sizeの戻り値を設定
    driver.get_window_size.return_value = {'width': 1200, 'height': 800}
    # スクリプト実行の戻り値を設定
    driver.execute_script.side_effect = [1000, 1500]  # height, widthの順
    return driver

@pytest.fixture
def mock_element():
    """WebElementのモックを作成するフィクスチャ"""
    element = MagicMock(spec=WebElement)
    element.is_displayed.return_value = True
    return element

def test_take_fullpage_screenshot(mock_driver):
    """take_fullpage_screenshotのテスト"""
    filename = "test_screenshot.png"

    # 関数実行
    result = take_fullpage_screenshot(mock_driver, filename)

    # 戻り値の確認
    assert result == filename

    # ページのサイズを取得していることを確認
    mock_driver.execute_script.assert_any_call("return document.body.scrollHeight")
    mock_driver.execute_script.assert_any_call("return document.body.scrollWidth")

    # ウィンドウサイズを設定していることを確認
    mock_driver.set_window_size.assert_any_call(1500, 1000)

    # スクリーンショットを撮っていることを確認
    mock_driver.save_screenshot.assert_called_once_with(filename)

    # 元のウィンドウサイズに戻していることを確認
    mock_driver.set_window_size.assert_any_call(1200, 800)

def test_take_element_screenshot(mock_driver, mock_element):
    """take_element_screenshotのテスト"""
    filename = "test_element_screenshot.png"

    # WebDriverWaitをモック
    with patch("selixir.screenshot.WebDriverWait") as mock_wait:
        # 関数実行
        result = take_element_screenshot(mock_driver, mock_element, filename)

        # 戻り値の確認
        assert result == filename

        # 要素が表示されるまで待機していることを確認
        mock_driver.execute_script.assert_called_once_with("arguments[0].scrollIntoView(true);", mock_element)
        mock_wait.assert_called_once_with(mock_driver, 5)
        mock_wait.return_value.until.assert_called_once()

        # 要素のスクリーンショットを撮っていることを確認
        mock_element.screenshot.assert_called_once_with(filename)
