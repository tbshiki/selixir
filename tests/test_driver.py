import pytest
import logging
from unittest.mock import MagicMock, patch
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException, WebDriverException
from selixir.driver import (
    debug,
    perform_control_click,
    switch_to_rightmost_tab,
    switch_to_new_tab,
    open_new_tab,
    close_other_tabs,
    wait_with_buffer,
    driver_start
)

@pytest.fixture
def mock_driver():
    """ChromeDriverのモックを作成するフィクスチャ"""
    driver = MagicMock(spec=webdriver.Chrome)
    driver.window_handles = ["handle1"]
    driver.current_window_handle = "handle1"
    return driver

@pytest.fixture
def mock_element():
    """WebElementのモックを作成するフィクスチャ"""
    return MagicMock(spec=WebElement)

def test_perform_control_click_success(mock_driver, mock_element):
    """perform_control_clickが新しいタブを開く場合のテスト"""
    # 初期状態では1つのタブ
    mock_driver.window_handles = ["handle1"]

    # クリック後に新しいタブが追加される状態をシミュレート
    def update_handles(*args):
        mock_driver.window_handles = ["handle1", "handle2"]
        return True

    mock_driver.execute_script = MagicMock()
    with patch("selixir.driver.WebDriverWait") as mock_wait:
        mock_wait.return_value.until.side_effect = update_handles

        result = perform_control_click(mock_driver, mock_element)

        assert result is True
        mock_driver.execute_script.assert_called_once()
        mock_wait.assert_called_once()

def test_perform_control_click_timeout(mock_driver, mock_element):
    """perform_control_clickがタイムアウトする場合のテスト"""
    mock_driver.execute_script = MagicMock()
    with patch("selixir.driver.WebDriverWait") as mock_wait:
        mock_wait.return_value.until.side_effect = TimeoutException()

        result = perform_control_click(mock_driver, mock_element)

        assert result is False
        mock_driver.execute_script.assert_called_once()

def test_switch_to_rightmost_tab_success(mock_driver, mock_element):
    """switch_to_rightmost_tabが成功する場合のテスト"""
    mock_driver.window_handles = ["handle1"]

    def update_handles(*args):
        mock_driver.window_handles = ["handle1", "handle2"]
        return True

    mock_driver.execute_script = MagicMock()
    with patch("selixir.driver.WebDriverWait") as mock_wait:
        mock_wait.return_value.until.side_effect = update_handles

        result = switch_to_rightmost_tab(mock_driver, mock_element)

        assert result is True
        mock_driver.switch_to.window.assert_called_once_with("handle2")

def test_switch_to_rightmost_tab_failure(mock_driver, mock_element):
    """switch_to_rightmost_tabが失敗する場合のテスト"""
    mock_driver.window_handles = ["handle1"]
    mock_driver.execute_script = MagicMock()

    with patch("selixir.driver.WebDriverWait") as mock_wait:
        mock_wait.return_value.until.side_effect = TimeoutException()

        result = switch_to_rightmost_tab(mock_driver, mock_element)

        assert result is False
        mock_driver.switch_to.window.assert_not_called()

def test_switch_to_new_tab_success(mock_driver, mock_element):
    """switch_to_new_tabが成功する場合のテスト"""
    mock_driver.window_handles = ["handle1"]

    def update_handles(*args):
        mock_driver.window_handles = ["handle1", "handle2"]
        return True

    mock_driver.execute_script = MagicMock()
    with patch("selixir.driver.WebDriverWait") as mock_wait:
        mock_wait.return_value.until.side_effect = update_handles

        result = switch_to_new_tab(mock_driver, mock_element)

        assert result is True
        mock_driver.switch_to.window.assert_called_once_with("handle2")

def test_switch_to_new_tab_failure(mock_driver, mock_element):
    """switch_to_new_tabが失敗する場合のテスト"""
    mock_driver.window_handles = ["handle1"]
    mock_driver.execute_script = MagicMock()

    with patch("selixir.driver.WebDriverWait") as mock_wait:
        mock_wait.return_value.until.side_effect = TimeoutException()

        result = switch_to_new_tab(mock_driver, mock_element)

        assert result is False
        mock_driver.switch_to.window.assert_not_called()

def test_open_new_tab_success(mock_driver):
    """open_new_tabが成功する場合のテスト"""
    mock_driver.window_handles = ["handle1"]
    url = "https://example.com"

    def update_handles(*args):
        mock_driver.window_handles = ["handle1", "handle2"]
        return True

    with patch("selixir.driver.WebDriverWait") as mock_wait:
        mock_wait.return_value.until.side_effect = update_handles

        result = open_new_tab(mock_driver, url)

        assert result == ["handle2"]
        mock_driver.switch_to.window.assert_called_once_with("handle2")
        mock_driver.execute_script.assert_called_once_with("window.open('https://example.com');")

def test_open_new_tab_timeout(mock_driver):
    """open_new_tabがタイムアウトする場合のテスト"""
    mock_driver.window_handles = ["handle1"]
    url = "https://example.com"

    with patch("selixir.driver.WebDriverWait") as mock_wait:
        mock_wait.return_value.until.side_effect = TimeoutException()

        result = open_new_tab(mock_driver, url)

        assert result == []
        mock_driver.switch_to.window.assert_not_called()
        mock_driver.execute_script.assert_called_once_with("window.open('https://example.com');")

@pytest.fixture
def mock_driver_multiple_tabs():
    """複数タブを持つDriverのモックを作成するフィクスチャ"""
    driver = MagicMock(spec=webdriver.Chrome)
    driver.window_handles = ["tab1", "tab2", "tab3"]
    driver.current_window_handle = "tab2"
    return driver

def test_close_other_tabs_current_tab(mock_driver_multiple_tabs):
    """close_other_tabsで現在のタブを指定しない場合のテスト"""
    driver = mock_driver_multiple_tabs
    
    # 関数を実行
    result = close_other_tabs(driver)
    
    # 戻り値の確認（現在のタブハンドルが返されること）
    assert result == "tab2"
    
    # 各タブに切り替えて閉じる処理が行われたことを確認
    expected_calls = [
        ("tab1", True),  # tab1に切り替えて閉じる
        ("tab3", True),  # tab3に切り替えて閉じる
        ("tab2", False)  # 現在のタブに戻る（閉じない）
    ]
    
    # 切り替えと閉じる操作の回数を確認
    assert driver.switch_to.window.call_count == 3
    assert driver.close.call_count == 2
    
    # 各タブの処理順序を確認
    for i, (tab, should_close) in enumerate(expected_calls):
        # i番目の呼び出しでタブtabに切り替えていることを確認
        assert driver.switch_to.window.call_args_list[i][0][0] == tab
        # should_closeがTrueなら閉じる操作が行われていることを確認
        if should_close:
            assert tab != "tab2"  # 現在のタブは閉じないことを確認

def test_close_other_tabs_specified_tab(mock_driver_multiple_tabs):
    """close_other_tabsで特定のタブを指定した場合のテスト"""
    driver = mock_driver_multiple_tabs
    
    # 関数を実行（tab1を残すよう指定）
    result = close_other_tabs(driver, current_tab_handle="tab1")
    
    # 戻り値の確認（指定したタブハンドルが返されること）
    assert result == "tab1"
    
    # 各タブに切り替えて閉じる処理が行われたことを確認
    expected_switch_calls = [
        ("tab2", True),  # tab2に切り替えて閉じる
        ("tab3", True),  # tab3に切り替えて閉じる
        ("tab1", False)  # 指定したタブに戻る（閉じない）
    ]
    
    # 切り替えと閉じる操作の回数を確認
    assert driver.switch_to.window.call_count == 3
    assert driver.close.call_count == 2
    
    # 最後に指定したタブに切り替えていることを確認
    assert driver.switch_to.window.call_args_list[-1][0][0] == "tab1"

def test_close_other_tabs_single_tab(mock_driver_multiple_tabs):
    """close_other_tabsでタブが1つしかない場合のテスト"""
    driver = mock_driver_multiple_tabs
    # タブが1つだけの状態に設定
    driver.window_handles = ["tab1"]
    driver.current_window_handle = "tab1"
    
    # 関数を実行
    result = close_other_tabs(driver)
    
    # 戻り値の確認
    assert result == "tab1"
    
    # closeが呼ばれていないことを確認（閉じるタブがない）
    driver.close.assert_not_called()
    
    # 最後に現在のタブに切り替えていることを確認
    driver.switch_to.window.assert_called_once_with("tab1")

@pytest.fixture
def mock_driver_for_wait():
    """WebDriverのモックを作成するフィクスチャ"""
    driver = MagicMock(spec=webdriver.Chrome)
    # execute_scriptの戻り値を設定
    driver.execute_script.return_value = "complete"  # document.readyStateの戻り値
    return driver

def test_wait_with_buffer_success(mock_driver_for_wait):
    """wait_with_bufferが正常に動作する場合のテスト"""
    # WebDriverWaitをモック
    with patch("selixir.driver.WebDriverWait") as mock_wait, \
         patch("selixir.driver.time.sleep") as mock_sleep, \
         patch("selixir.driver.random.uniform", return_value=1.5) as mock_uniform:
        
        # 関数実行
        wait_with_buffer(mock_driver_for_wait, time_sleep=1, buffer_time=0.5, base_wait=10)
        
        # WebDriverWaitが正しく使用されていることを確認
        mock_wait.assert_called_once_with(mock_driver_for_wait, 10)
        mock_wait.return_value.until.assert_called_once()
        
        # ランダム待機時間が計算されていることを確認
        mock_uniform.assert_called_once_with(1, 1.5)
        
        # 計算された時間だけsleepしていることを確認
        mock_sleep.assert_called_once_with(1.5)

def test_wait_with_buffer_timeout(mock_driver_for_wait):
    """wait_with_bufferでページロード待機がタイムアウトする場合のテスト"""
    # WebDriverWaitをモック（タイムアウト例外を発生させる）
    with patch("selixir.driver.WebDriverWait") as mock_wait, \
         patch("selixir.driver.time.sleep") as mock_sleep:
        mock_wait.return_value.until.side_effect = TimeoutException("Timeout")
        
        # 関数実行（例外が発生しないことを確認）
        wait_with_buffer(mock_driver_for_wait)
        
        # WebDriverWaitが呼ばれていることを確認
        mock_wait.assert_called_once()
        
        # タイムアウトしたのでsleepは呼ばれないはず
        mock_sleep.assert_not_called()

def test_wait_with_buffer_other_exception(mock_driver_for_wait):
    """wait_with_bufferでその他の例外が発生する場合のテスト"""
    # WebDriverWaitをモック（一般的な例外を発生させる）
    with patch("selixir.driver.WebDriverWait") as mock_wait, \
         patch("selixir.driver.time.sleep") as mock_sleep:
        mock_wait.return_value.until.side_effect = Exception("Something went wrong")
        
        # 関数実行（例外が発生しないことを確認）
        wait_with_buffer(mock_driver_for_wait)
        
        # WebDriverWaitが呼ばれていることを確認
        mock_wait.assert_called_once()
        
        # 例外発生でsleepは呼ばれないはず
        mock_sleep.assert_not_called()

def test_wait_with_buffer_custom_parameters(mock_driver_for_wait):
    """wait_with_bufferでカスタムパラメータを指定した場合のテスト"""
    with patch("selixir.driver.WebDriverWait") as mock_wait, \
         patch("selixir.driver.time.sleep") as mock_sleep, \
         patch("selixir.driver.random.uniform", return_value=4.2) as mock_uniform:
        
        # カスタムパラメータで関数実行
        wait_with_buffer(mock_driver_for_wait, time_sleep=3, buffer_time=2, base_wait=15)
        
        # WebDriverWaitが正しいパラメータで呼ばれていることを確認
        mock_wait.assert_called_once_with(mock_driver_for_wait, 15)
        
        # ランダム待機時間が正しいパラメータで計算されていることを確認
        mock_uniform.assert_called_once_with(3, 5)  # time_sleep + buffer_time
        
        # 計算された時間だけsleepしていることを確認
        mock_sleep.assert_called_once_with(4.2)  # ランダムで生成された値

@pytest.fixture
def mock_logger():
    """ロガーのモックを作成するフィクスチャ"""
    with patch("selixir.driver.logger") as mock_logger:
        yield mock_logger

def test_debug_enable(mock_logger):
    """debug関数でデバッグモードを有効にした場合のテスト"""
    # StreamHandlerとFormatterのモックを作成
    with patch("selixir.driver.logging.StreamHandler") as mock_handler_class, \
         patch("selixir.driver.logging.Formatter") as mock_formatter_class:
        
        # モックインスタンスを作成
        mock_handler = MagicMock()
        mock_formatter = MagicMock()
        mock_handler_class.return_value = mock_handler
        mock_formatter_class.return_value = mock_formatter
        
        # 関数実行
        debug(enable=True)
        
        # ロガーレベルの設定確認
        mock_logger.setLevel.assert_called_with(logging.DEBUG)
        
        # ハンドラとフォーマッタの追加確認
        mock_formatter_class.assert_called_once()
        mock_handler.setFormatter.assert_called_once_with(mock_formatter)
        mock_logger.addHandler.assert_called_once_with(mock_handler)

def test_debug_disable(mock_logger):
    """debug関数でデバッグモードを無効にした場合のテスト"""
    # モックハンドラを作成
    mock_handler1 = MagicMock(spec=logging.StreamHandler)
    mock_handler2 = MagicMock(spec=logging.NullHandler)
    mock_handler3 = MagicMock(spec=logging.StreamHandler)
    
    # ロガーのハンドラリストをモック
    mock_logger.handlers = [mock_handler1, mock_handler2, mock_handler3]
    
    # 関数実行
    debug(enable=False)
    
    # ロガーレベルの設定確認
    mock_logger.setLevel.assert_called_with(logging.WARNING)
    
    # StreamHandlerが削除されたことを確認
    assert mock_logger.removeHandler.call_count == 2
    mock_logger.removeHandler.assert_any_call(mock_handler1)
    mock_logger.removeHandler.assert_any_call(mock_handler3)

def test_debug_default(mock_logger):
    """debug関数のデフォルトパラメータのテスト"""
    # 関数実行（デフォルトはFalse）
    debug()
    
    # ロガーレベルの設定確認
    mock_logger.setLevel.assert_called_with(logging.WARNING)

@pytest.fixture
def mock_chrome_for_driver_start():
    """Chromeブラウザのモックを作成するフィクスチャ"""
    with patch("selenium.webdriver.Chrome") as mock_chrome_class:
        # モックインスタンスを作成
        mock_driver = MagicMock(spec=webdriver.Chrome)
        mock_chrome_class.return_value = mock_driver
        yield mock_chrome_class, mock_driver

@pytest.fixture
def mock_chrome_driver_manager():
    """ChromeDriverManagerのモックを作成するフィクスチャ"""
    with patch("selixir.driver.ChromeDriverManager") as mock_cdm_class:
        mock_cdm = MagicMock()
        mock_cdm.install.return_value = "/path/to/chromedriver"
        mock_cdm_class.return_value = mock_cdm
        yield mock_cdm_class, mock_cdm

@pytest.fixture
def mock_wait_with_buffer_for_driver():
    """wait_with_buffer関数のモックを作成するフィクスチャ"""
    with patch("selixir.driver.wait_with_buffer") as mock_wait:
        yield mock_wait

def test_driver_start_normal(mock_chrome_for_driver_start, mock_wait_with_buffer_for_driver):
    """driver_startが正常に動作する場合のテスト（通常モード）"""
    mock_chrome_class, mock_driver = mock_chrome_for_driver_start
    
    # 関数を実行
    result = driver_start("https://example.com")
    
    # 戻り値の確認
    assert result == mock_driver
    
    # Chromeオプションの設定を確認（全てではなく主要な設定のみ）
    options_arg = mock_chrome_class.call_args[1]["options"]
    assert isinstance(options_arg, webdriver.ChromeOptions)
    
    # ブラウザの基本設定確認
    mock_driver.maximize_window.assert_called_once()
    mock_driver.get.assert_called_once_with("https://example.com")
    
    # wait_with_bufferが呼ばれたことを確認
    assert mock_wait_with_buffer_for_driver.call_count == 2

def test_driver_start_heroku_mode_boolean(mock_chrome_for_driver_start, mock_wait_with_buffer_for_driver):
    """driver_startがheroku_mode=Trueで動作する場合のテスト"""
    mock_chrome_class, mock_driver = mock_chrome_for_driver_start
    
    # 関数を実行（heroku_mode=True）
    result = driver_start("https://example.com", heroku_mode=True)
    
    # 戻り値の確認
    assert result == mock_driver
    
    # Herokuモード用のオプションが設定されているか確認
    options_arg = mock_chrome_class.call_args[1]["options"]
    # --headless=newと--no-sandboxは少なくとも含まれているはず
    arguments = [arg for arg in options_arg.arguments if "--headless=new" in arg or "--no-sandbox" in arg]
    assert len(arguments) >= 2

def test_driver_start_heroku_mode_string(mock_chrome_for_driver_start, mock_wait_with_buffer_for_driver):
    """driver_startがheroku_mode='true'で動作する場合のテスト"""
    mock_chrome_class, mock_driver = mock_chrome_for_driver_start
    
    # 関数を実行（heroku_mode='true'）
    result = driver_start("https://example.com", heroku_mode="true")
    
    # 戻り値の確認
    assert result == mock_driver
    
    # Herokuモード用のオプションが設定されているか確認
    options_arg = mock_chrome_class.call_args[1]["options"]
    # --headless=newと--no-sandboxは少なくとも含まれているはず
    arguments = [arg for arg in options_arg.arguments if "--headless=new" in arg or "--no-sandbox" in arg]
    assert len(arguments) >= 2

def test_driver_start_fallback(mock_chrome_for_driver_start, mock_chrome_driver_manager, mock_wait_with_buffer_for_driver):
    """driver_startが初回失敗し、ChromeDriverManagerでフォールバックする場合のテスト"""
    mock_chrome_class, mock_driver = mock_chrome_for_driver_start
    mock_cdm_class, mock_cdm = mock_chrome_driver_manager
    
    # 1回目の初期化で例外を発生させる
    mock_chrome_class.side_effect = [WebDriverException("Chrome initialization failed"), mock_driver]
    
    # 関数を実行
    result = driver_start("https://example.com")
    
    # 戻り値の確認
    assert result == mock_driver
    
    # ChromeDriverManagerが使用されたことを確認
    mock_cdm.install.assert_called_once()
    
    # Serviceが作成されたことを確認（2回目の呼び出し）
    assert mock_chrome_class.call_count == 2
    assert "service" in mock_chrome_class.call_args[1]
    
    # ブラウザの基本設定確認
    mock_driver.maximize_window.assert_called_once()
    mock_driver.get.assert_called_once_with("https://example.com")
