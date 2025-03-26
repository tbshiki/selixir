import os
import time


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
        print(f"Unexpected error getting latest file in {directory}: {e}")
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
