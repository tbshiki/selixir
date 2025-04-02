import pytest
import os
import time
from unittest.mock import MagicMock, patch, mock_open
from selixir.file import (
    _validate_directory,
    _get_latest_file_from_list,
    get_latest_file_path,
    wait_for_new_file,
    wait_for_download_completion
)

@pytest.fixture
def mock_directory():
    """ディレクトリのモックを設定するフィクスチャ"""
    with patch("os.path.exists") as mock_exists, \
         patch("os.path.isdir") as mock_isdir:
        mock_exists.return_value = True
        mock_isdir.return_value = True
        yield "/path/to/mock/directory"

def test_validate_directory_success(mock_directory):
    """_validate_directoryが成功する場合のテスト"""
    # 例外が発生しないことを確認
    _validate_directory(mock_directory)

def test_validate_directory_not_exists():
    """_validate_directoryでディレクトリが存在しない場合のテスト"""
    with patch("os.path.exists", return_value=False):
        with pytest.raises(FileNotFoundError):
            _validate_directory("/not/exists")

def test_validate_directory_not_a_directory():
    """_validate_directoryでパスがディレクトリでない場合のテスト"""
    with patch("os.path.exists", return_value=True), \
         patch("os.path.isdir", return_value=False):
        with pytest.raises(NotADirectoryError):
            _validate_directory("/path/to/file.txt")

def test_get_latest_file_from_list_empty():
    """_get_latest_file_from_listで空リストを渡した場合のテスト"""
    result = _get_latest_file_from_list([], "/some/dir")
    assert result is None

def test_get_latest_file_from_list_success():
    """_get_latest_file_from_listが成功する場合のテスト"""
    file_list = ["file1.txt", "file2.txt", "file3.txt"]
    directory = "/test/dir"

    # パスジョインの結果を事前に定義
    full_paths = {
        "file1.txt": "/test/dir/file1.txt",
        "file2.txt": "/test/dir/file2.txt",
        "file3.txt": "/test/dir/file3.txt"
    }

    # os.path.joinとos.path.getctimeの戻り値を設定
    with patch("os.path.join", side_effect=lambda dir, file: full_paths[file]) as mock_join, \
         patch("os.path.getctime") as mock_getctime:
        # file2.txtが最新になるように設定
        mock_getctime.side_effect = lambda path: {
            "/test/dir/file1.txt": 100,
            "/test/dir/file2.txt": 300,
            "/test/dir/file3.txt": 200
        }[path]

        result = _get_latest_file_from_list(file_list, directory)
        assert result == "/test/dir/file2.txt"

def test_get_latest_file_from_list_exception():
    """_get_latest_file_from_listで例外が発生する場合のテスト"""
    file_list = ["file1.txt", "file2.txt"]
    directory = "/test/dir"

    with patch("os.path.getctime", side_effect=Exception("Test exception")):
        result = _get_latest_file_from_list(file_list, directory)
        assert result is None

def test_get_latest_file_path_success(mock_directory):
    """get_latest_file_pathが成功する場合のテスト"""
    # os.listdirの戻り値を設定
    with patch("os.listdir") as mock_listdir, \
         patch("os.path.isfile", return_value=True), \
         patch("selixir.file._get_latest_file_from_list") as mock_get_latest:
        mock_listdir.return_value = ["file1.txt", "file2.txt", "temp.crdownload"]
        mock_get_latest.return_value = "/path/to/mock/directory/file2.txt"

        result = get_latest_file_path(mock_directory)

        # 一時ファイルが除外されていることを確認
        filtered_files = ["file1.txt", "file2.txt"]  # temp.crdownloadは除外される
        mock_get_latest.assert_called_once_with(filtered_files, mock_directory)

        assert result == "/path/to/mock/directory/file2.txt"

def test_get_latest_file_path_no_files(mock_directory):
    """get_latest_file_pathでファイルが見つからない場合のテスト"""
    with patch("os.listdir", return_value=[]), \
         patch("selixir.file._get_latest_file_from_list") as mock_get_latest:
        mock_get_latest.return_value = None

        result = get_latest_file_path(mock_directory)
        assert result is None

def test_get_latest_file_path_permission_error(mock_directory):
    """get_latest_file_pathでPermissionErrorが発生する場合のテスト"""
    with patch("os.listdir", side_effect=PermissionError("Permission denied")):
        with pytest.raises(PermissionError):
            get_latest_file_path(mock_directory)

def test_wait_for_new_file_success(mock_directory):
    """wait_for_new_fileが成功する場合のテスト"""
    with patch("selixir.file.get_latest_file_path") as mock_get_latest, \
         patch("selixir.file.time.sleep", return_value=None):
        # 最初はNone、次に新しいファイルパスを返す
        mock_get_latest.side_effect = [None, "/path/to/mock/directory/new_file.txt"]

        result = wait_for_new_file(mock_directory, timeout_seconds=5)

        assert result == "/path/to/mock/directory/new_file.txt"
        assert mock_get_latest.call_count == 2

def test_wait_for_new_file_with_previous(mock_directory):
    """wait_for_new_fileで前のファイルを指定した場合のテスト"""
    with patch("selixir.file.get_latest_file_path") as mock_get_latest, \
         patch("selixir.file.time.sleep", return_value=None):
        previous_path = "/path/to/mock/directory/old_file.txt"

        # 最初は前のファイル、次に新しいファイルパスを返す
        mock_get_latest.side_effect = [previous_path, "/path/to/mock/directory/new_file.txt"]

        result = wait_for_new_file(mock_directory, timeout_seconds=5, previous_path=previous_path)

        assert result == "/path/to/mock/directory/new_file.txt"
        assert mock_get_latest.call_count == 2

def test_wait_for_new_file_timeout(mock_directory):
    """wait_for_new_fileでタイムアウトする場合のテスト"""
    with patch("selixir.file.get_latest_file_path", return_value=None), \
         patch("selixir.file.time.sleep", return_value=None), \
         patch("selixir.file.time.time") as mock_time:
        # タイムアウトをシミュレート
        mock_time.side_effect = [100, 105, 110]  # start, check, end (> start + timeout)

        with pytest.raises(Exception, match="No new file found"):
            wait_for_new_file(mock_directory, timeout_seconds=5)

def test_wait_for_download_completion_success(mock_directory):
    """wait_for_download_completionが成功する場合のテスト"""
    before_files = {"old_file1.txt", "old_file2.txt"}

    with patch("os.listdir") as mock_listdir, \
         patch("selixir.file._get_latest_file_from_list") as mock_get_latest, \
         patch("selixir.file.time.sleep", return_value=None), \
         patch("selixir.file.time.time") as mock_time:

        # タイムアウトしないようにシミュレート
        mock_time.side_effect = [100, 105]  # start, check (< start + timeout)

        # ファイルリストをシミュレート（新しいファイルが追加される）
        mock_listdir.return_value = ["old_file1.txt", "old_file2.txt", "new_file.txt"]

        # 最新ファイルを返す
        mock_get_latest.return_value = "/path/to/mock/directory/new_file.txt"

        result = wait_for_download_completion(mock_directory, before_files, timeout=30)

        assert result == "/path/to/mock/directory/new_file.txt"
        assert mock_listdir.called
        mock_get_latest.assert_called_once_with(["new_file.txt"], mock_directory)

def test_wait_for_download_completion_timeout(mock_directory):
    """wait_for_download_completionでタイムアウトする場合のテスト"""
    before_files = {"old_file1.txt", "old_file2.txt"}

    with patch("os.listdir") as mock_listdir, \
         patch("selixir.file.time.sleep", return_value=None), \
         patch("selixir.file.time.time") as mock_time:

        # タイムアウトをシミュレート - 十分な数の値を返す
        mock_time.side_effect = [100, 105, 110, 115, 120, 125, 130, 135, 200]  # 十分な数の値

        # ファイルが追加されない
        mock_listdir.return_value = ["old_file1.txt", "old_file2.txt"]

        with pytest.raises(TimeoutError, match="Download did not complete"):
            wait_for_download_completion(mock_directory, before_files, timeout=30)

def test_wait_for_download_completion_file_after_timeout(mock_directory):
    """wait_for_download_completionでタイムアウト後にファイルが見つかる場合のテスト"""
    before_files = {"old_file1.txt", "old_file2.txt"}

    with patch("os.listdir") as mock_listdir, \
         patch("selixir.file._get_latest_file_from_list") as mock_get_latest, \
         patch("selixir.file.time.sleep", return_value=None), \
         patch("selixir.file.time.time") as mock_time:

        # タイムアウトをシミュレート - 十分な数の値を返す
        mock_time.side_effect = [100, 105, 110, 115, 120, 125, 130, 135, 200]  # 十分な数の値

        # タイムアウト後にファイルが追加される
        mock_listdir.side_effect = [
            ["old_file1.txt", "old_file2.txt"],  # タイムアウト中
            ["old_file1.txt", "old_file2.txt", "new_file.txt"]  # タイムアウト後のチェック
        ]

        # 最新ファイルを返す
        mock_get_latest.return_value = "/path/to/mock/directory/new_file.txt"

        result = wait_for_download_completion(mock_directory, before_files, timeout=30)

        assert result == "/path/to/mock/directory/new_file.txt"
        assert mock_listdir.call_count == 2
        mock_get_latest.assert_called_once_with(["new_file.txt"], mock_directory)
