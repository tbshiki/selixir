import pytest
from unittest.mock import MagicMock, patch
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selixir.scroll import scroll_to_element_by_js, scroll_to_target

@pytest.fixture
def mock_driver():
    """WebDriverのモックを作成するフィクスチャ"""
    driver = MagicMock(spec=webdriver.Chrome)
    return driver

@pytest.fixture
def mock_element():
    """WebElementのモックを作成するフィクスチャ"""
    element = MagicMock(spec=WebElement)
    element.location = {"y": 500}
    element.is_displayed.return_value = True
    return element

def test_scroll_to_element_by_js(mock_driver, mock_element):
    """scroll_to_element_by_jsのテスト"""
    # 関数実行
    scroll_to_element_by_js(mock_driver, mock_element, top_offset=100)

    # JavaScriptが正しく実行されていることを確認
    mock_driver.execute_script.assert_called_once_with("window.scrollTo(0, 400);")

def test_scroll_to_element_by_js_zero_offset(mock_driver, mock_element):
    """scroll_to_element_by_jsのオフセットゼロのテスト"""
    # 関数実行
    scroll_to_element_by_js(mock_driver, mock_element, top_offset=0)

    # JavaScriptが正しく実行されていることを確認
    mock_driver.execute_script.assert_called_once_with("window.scrollTo(0, 500);")

def test_scroll_to_element_by_js_negative_result(mock_driver):
    """scroll_to_element_by_jsの計算結果が負になる場合のテスト"""
    element = MagicMock(spec=WebElement)
    element.location = {"y": 50}  # 小さな値

    # 関数実行
    scroll_to_element_by_js(mock_driver, element, top_offset=100)

    # 負の値にならずにゼロになることを確認
    mock_driver.execute_script.assert_called_once_with("window.scrollTo(0, 0);")

def test_scroll_to_target_with_element(mock_driver, mock_element):
    """scroll_to_targetに要素を渡した場合のテスト"""
    with patch("selixir.scroll.ActionChains") as mock_actions_class, \
         patch("selixir.scroll.WebDriverWait") as mock_wait:
        # ActionChains
        mock_actions = MagicMock()
        mock_actions_class.return_value = mock_actions
        move_chain = MagicMock()
        mock_actions.move_to_element.return_value = move_chain

        # 関数実行
        scroll_to_target(mock_driver, mock_element)

        # ActionChainsが正しく実行されていることを確認
        mock_actions_class.assert_called_once_with(mock_driver)
        mock_actions.move_to_element.assert_called_once_with(mock_element)
        move_chain.perform.assert_called_once()

        # WebDriverWaitが正しく使われていることを確認
        mock_wait.assert_called_once_with(mock_driver, 1)
        mock_wait.return_value.until.assert_called_once()

def test_scroll_to_target_with_xpath(mock_driver, mock_element):
    """scroll_to_targetにXPathを渡した場合のテスト"""
    xpath = "//div[@id='target']"

    # find_elementの戻り値を設定
    mock_driver.find_element.return_value = mock_element

    with patch("selixir.scroll.ActionChains") as mock_actions_class, \
         patch("selixir.scroll.WebDriverWait") as mock_wait:
        # ActionChains
        mock_actions = MagicMock()
        mock_actions_class.return_value = mock_actions
        move_chain = MagicMock()
        mock_actions.move_to_element.return_value = move_chain

        # 関数実行
        scroll_to_target(mock_driver, xpath)

        # 要素が正しく検索されていることを確認
        mock_driver.find_element.assert_called_once_with(By.XPATH, xpath)

        # ActionChainsが正しく実行されていることを確認
        mock_actions_class.assert_called_once_with(mock_driver)
        mock_actions.move_to_element.assert_called_once_with(mock_element)
        move_chain.perform.assert_called_once()

def test_scroll_to_target_element_not_found(mock_driver):
    """scroll_to_targetで要素が見つからない場合のテスト"""
    xpath = "//div[@id='not-exist']"

    # find_elementが例外を投げるように設定
    mock_driver.find_element.side_effect = NoSuchElementException("Element not found")

    # 関数実行（例外が発生しないことを確認）
    scroll_to_target(mock_driver, xpath)

    # find_elementが呼ばれたことを確認
    mock_driver.find_element.assert_called_once_with(By.XPATH, xpath)

def test_scroll_to_target_raise_on_failure(mock_driver):
    """scroll_to_targetでraise_on_failure=Trueの場合のテスト"""
    xpath = "//div[@id='not-exist']"

    # find_elementが例外を投げるように設定
    mock_driver.find_element.side_effect = NoSuchElementException("Element not found")

    # 例外が発生することを確認
    with pytest.raises(NoSuchElementException):
        scroll_to_target(mock_driver, xpath, raise_on_failure=True)

def test_scroll_to_target_timeout(mock_driver, mock_element):
    """scroll_to_targetでタイムアウトが発生する場合のテスト"""
    with patch("selixir.scroll.ActionChains") as mock_actions_class, \
         patch("selixir.scroll.WebDriverWait") as mock_wait:
        # ActionChains
        mock_actions = MagicMock()
        mock_actions_class.return_value = mock_actions
        move_chain = MagicMock()
        mock_actions.move_to_element.return_value = move_chain

        # WebDriverWaitがタイムアウトする
        mock_wait.return_value.until.side_effect = TimeoutException("Timeout")

        # 関数実行（例外が発生しないことを確認）
        scroll_to_target(mock_driver, mock_element)

        # ActionChainsが正しく実行されていることを確認
        mock_actions_class.assert_called_once_with(mock_driver)
        move_chain.perform.assert_called_once()

        # WebDriverWaitが呼ばれたことを確認
        mock_wait.assert_called_once()

def test_scroll_to_target_action_fails_fallback_to_js(mock_driver, mock_element):
    """scroll_to_targetでActionChainsが失敗してJavaScriptにフォールバックする場合のテスト"""
    with patch("selixir.scroll.ActionChains") as mock_actions_class, \
         patch("selixir.scroll.scroll_to_element_by_js") as mock_js_scroll:
        # ActionChainsが例外を投げるように設定
        mock_actions = MagicMock()
        mock_actions_class.return_value = mock_actions
        mock_actions.move_to_element.side_effect = Exception("Action failed")

        # 関数実行
        scroll_to_target(mock_driver, mock_element, top_offset=150)

        # JavaScriptスクロール関数が呼ばれたことを確認
        mock_js_scroll.assert_called_once_with(mock_driver, mock_element, 150)

def test_scroll_to_target_empty_target():
    """scroll_to_targetで空のターゲットを渡した場合のテスト"""
    mock_driver = MagicMock()

    # 空のターゲットで例外が発生することを確認
    with pytest.raises(ValueError):
        scroll_to_target(mock_driver, None)

    with pytest.raises(ValueError):
        scroll_to_target(mock_driver, "")
