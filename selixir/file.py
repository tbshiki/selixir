import os
import time
import logging

# Get the logger
logger = logging.getLogger("selixir")


def get_latest_file_path(directory):
    """
    Get the most recently modified file in the directory.

    Args:
        directory: The directory to search in.

    Returns:
        The path of the latest file, or None if no files exist or an error occurs.

    Raises:
        FileNotFoundError: If the directory does not exist.
        PermissionError: If there is a permission issue accessing the directory.
    """
    if not os.path.exists(directory):
        raise FileNotFoundError(f"Directory does not exist: {directory}")

    if not os.path.isdir(directory):
        raise NotADirectoryError(f"Path is not a directory: {directory}")

    try:
        files = [os.path.join(directory, f) for f in os.listdir(directory) if not f.endswith((".crdownload", ".tmp")) and os.path.isfile(os.path.join(directory, f))]

        if not files:
            return None

        return max(files, key=os.path.getctime)
    except ValueError:
        return None
    except PermissionError as e:
        raise PermissionError(f"Permission denied accessing directory: {directory}") from e
    except Exception as e:
        logger.error(f"Unexpected error getting latest file in {directory}: {e}")
        return None


def wait_for_new_file(directory, timeout_seconds=30, previous_path=None):
    """
    Wait for a new file to appear in the directory.

    Args:
        directory: The directory to search in.
        timeout_seconds: The maximum time to wait for a new file to appear.
        previous_path: The path of the previously latest file, if any.

    Returns:
        The path of the new file, or raises an exception if the timeout is exceeded.
    """
    end_time = time.time() + timeout_seconds
    while time.time() < end_time:
        latest_file = get_latest_file_path(directory)
        if previous_path is None:
            if latest_file:
                return latest_file  # Return the first valid file found
        else:
            if latest_file and latest_file != previous_path:
                return latest_file  # Return a new file if it's different from previous_path

        time.sleep(1)

    raise Exception(f"No new file found in {directory} within {timeout_seconds} seconds.")


def wait_for_download_completion(directory, before_files, timeout=60):
    """
    Get newly downloaded and completed files in the specified directory.

    Args:
        directory: The directory to watch for downloads
        before_files: Set of files that existed before the download started
        timeout: Maximum wait time in seconds (default: 60)

    Returns:
        The path to the most recently downloaded file

    Raises:
        FileNotFoundError: If the directory does not exist
        NotADirectoryError: If the path is not a directory
        TimeoutError: If no download completes within the timeout period
    """
    if not os.path.exists(directory):
        raise FileNotFoundError(f"Directory does not exist: {directory}")

    if not os.path.isdir(directory):
        raise NotADirectoryError(f"Path is not a directory: {directory}")

    logger.info(f"Waiting for download completion (max wait time: {timeout} seconds)...")

    end_time = time.time() + timeout
    check_count = 0
    last_files_count = len(before_files)

    while time.time() < end_time:
        time.sleep(1)
        check_count += 1

        try:
            # 一時ファイルを除外して、現在のファイル一覧を取得
            current_files = set(f for f in os.listdir(directory) if not f.endswith((".crdownload", ".tmp", "part")))

            # 進行状況ログ（30秒ごと）
            if check_count % 30 == 0:
                if len(current_files) > last_files_count:
                    logger.info(f"New files detected. Currently {len(current_files)} files.")
                    last_files_count = len(current_files)
                else:
                    logger.debug(f"Waiting for download... {check_count} seconds elapsed")

            # 新しく作成されたファイルを取得
            new_files = current_files - before_files

            if new_files:
                new_files_list = list(new_files)
                logger.info(f"New files detected: {len(new_files_list)} files")

                # ダウンロード完了をさらに確認（完了確認のために3秒待機）
                time.sleep(3)

                # 最新のファイルを返す
                try:
                    latest_file = max((os.path.join(directory, f) for f in new_files), key=os.path.getctime)
                    logger.info(f"Download complete: {os.path.basename(latest_file)}")
                    return latest_file
                except ValueError as e:
                    logger.error(f"Failed to get latest file: {e}")
        except Exception as e:
            logger.error(f"Error while checking downloads: {e}")

    # タイムアウトした場合、存在するファイルを再確認
    try:
        current_files = set(f for f in os.listdir(directory) if not f.endswith((".crdownload", ".tmp", "part")))
        new_files = current_files - before_files

        if new_files:
            # タイムアウトしたが新規ファイルが見つかった場合
            latest_file = max((os.path.join(directory, f) for f in new_files), key=os.path.getctime)
            logger.warning(f"File found after timeout: {os.path.basename(latest_file)}")
            return latest_file
    except Exception as e:
        logger.error(f"Error checking files after timeout: {e}")

    # 全ての方法でファイルが見つからなかった場合
    error_msg = f"Download did not complete within {timeout} seconds."
    logger.error(error_msg)
    raise TimeoutError(error_msg)
