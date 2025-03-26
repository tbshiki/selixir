import os
import time
import logging

# Get the logger
logger = logging.getLogger("selixir")

# Constants
TEMP_FILE_EXTENSIONS = (".crdownload", ".tmp", ".part")


def _validate_directory(directory):
    """
    Internal function: Validate that directory exists and is actually a directory.

    Args:
        directory: The directory path to validate

    Raises:
        FileNotFoundError: If the directory does not exist
        NotADirectoryError: If the path is not a directory
    """
    if not os.path.exists(directory):
        raise FileNotFoundError(f"Directory does not exist: {directory}")

    if not os.path.isdir(directory):
        raise NotADirectoryError(f"Path is not a directory: {directory}")


def _get_latest_file_from_list(file_list, directory):
    """
    Internal function: Get the most recently modified file from a list of filenames.

    Args:
        file_list: List or set of filenames (not full paths)
        directory: The directory containing the files

    Returns:
        The full path of the latest file, or None if no files exist or an error occurs
    """
    if not file_list:
        return None

    try:
        return max((os.path.join(directory, f) for f in file_list), key=os.path.getctime)
    except ValueError:
        return None
    except Exception as e:
        logger.error(f"Error getting latest file from list: {e}")
        return None


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
    _validate_directory(directory)

    try:
        files = [f for f in os.listdir(directory) if not f.endswith(TEMP_FILE_EXTENSIONS) and os.path.isfile(os.path.join(directory, f))]

        return _get_latest_file_from_list(files, directory)
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

    Raises:
        FileNotFoundError: If the directory does not exist
        NotADirectoryError: If the path is not a directory
        Exception: If no new file is found within the timeout period
    """
    _validate_directory(directory)

    logger.debug(f"Waiting for new file in {directory} (timeout: {timeout_seconds}s)")

    end_time = time.time() + timeout_seconds
    while time.time() < end_time:
        latest_file = get_latest_file_path(directory)
        if previous_path is None:
            if latest_file:
                logger.info(f"Found file: {os.path.basename(latest_file)}")
                return latest_file  # Return the first valid file found
        else:
            if latest_file and latest_file != previous_path:
                logger.info(f"Found new file: {os.path.basename(latest_file)}")
                return latest_file  # Return a new file if it's different from previous_path

        time.sleep(1)

    error_msg = f"No new file found in {directory} within {timeout_seconds} seconds."
    logger.error(error_msg)
    raise Exception(error_msg)


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
    _validate_directory(directory)

    logger.info(f"Waiting for download completion (max wait time: {timeout} seconds)...")

    end_time = time.time() + timeout
    check_count = 0
    last_files_count = len(before_files)

    while time.time() < end_time:
        time.sleep(1)
        check_count += 1

        try:
            # Get the current file list, excluding temporary files
            current_files = set(f for f in os.listdir(directory) if not f.endswith(TEMP_FILE_EXTENSIONS))

            # Progress logging (every 30 seconds)
            if check_count % 30 == 0:
                if len(current_files) > last_files_count:
                    logger.info(f"New files detected. Currently {len(current_files)} files.")
                    last_files_count = len(current_files)
                else:
                    logger.debug(f"Waiting for download... {check_count} seconds elapsed")

            # Get newly created files
            new_files = current_files - before_files

            if new_files:
                new_files_list = list(new_files)
                logger.info(f"New files detected: {len(new_files_list)} files")

                # Additional wait to confirm download completion (3 seconds)
                time.sleep(3)

                # Return the latest file
                latest_file = _get_latest_file_from_list(new_files, directory)
                if latest_file:
                    logger.info(f"Download complete: {os.path.basename(latest_file)}")
                    return latest_file
                else:
                    logger.error("Failed to get latest file")
        except Exception as e:
            logger.error(f"Error while checking downloads: {e}")

    # If timed out, check existing files again
    try:
        current_files = set(f for f in os.listdir(directory) if not f.endswith(TEMP_FILE_EXTENSIONS))
        new_files = current_files - before_files

        if new_files:
            # File found after timeout
            latest_file = _get_latest_file_from_list(new_files, directory)
            if latest_file:
                logger.warning(f"File found after timeout: {os.path.basename(latest_file)}")
                return latest_file
    except Exception as e:
        logger.error(f"Error checking files after timeout: {e}")

    # If no files were found by any method
    error_msg = f"Download did not complete within {timeout} seconds."
    logger.error(error_msg)
    raise TimeoutError(error_msg)
