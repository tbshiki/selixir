# Selixir

Selixir is a lightweight wrapper library for Selenium WebDriver.
It provides useful utility functions to make browser automation easier and more robust.

## Features

- **Driver Management**: Easily start and configure ChromeDriver
- **Click Operation Control**: Manage link opening in new tabs and tab handling
- **Scroll Operations**: Scroll to elements in various ways
- **File Operations**: Provides useful functions for monitoring downloaded files

## Installation

```bash
pip install selixir
```

## Quick Start

```python
import selixir
from selenium.webdriver.common.by import By

# Enable debug mode to see logs
selixir.debug(True)

# Start ChromeDriver
driver = selixir.driver_start("https://example.com")

# Scroll to an element
element = driver.find_element(By.ID, "target-element")
selixir.scroll_to_target(driver, element)

# Open a link in a new tab
link_element = driver.find_element(By.XPATH, "//a[contains(text(), 'Link')]")
if selixir.switch_to_new_tab(driver, link_element):
    print("Switched to a new tab")

# Get the latest file in the download directory
download_dir = "/path/to/downloads"
latest_file = selixir.get_latest_file_path(download_dir)
```

## Main Features

### Customizing Log Output

```python
# When debug mode is enabled, logs are displayed on standard output
selixir.debug(True)  # Enable
selixir.debug(False) # Disable

# If you want to configure your own logger:
import logging

# Get the logger
selixir_logger = logging.getLogger("selixir")

# Configure your own log handler
file_handler = logging.FileHandler("selixir.log")
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
selixir_logger.addHandler(file_handler)
selixir_logger.setLevel(logging.DEBUG)  # Set log level
```

### Driver Management

```python
# Display logs during driver operations
selixir.debug(True)

# Start the driver
driver = selixir.driver_start(url)

# Start the driver with Heroku environment settings
driver = selixir.driver_start(url, heroku_mode=True)
```

### Tab Operations

```python
# Open a new tab
selixir.open_new_tab(driver, "https://example.com")

# Close all tabs except the current one
selixir.close_other_tabs(driver)

# Control+click a link to open in a new tab
element = driver.find_element(By.XPATH, "//a[@href='https://example.com']")
selixir.perform_control_click(driver, element)

# Control+click and switch to the new tab
success = selixir.switch_to_new_tab(driver, element)
if success:
    print('Switched to a new tab')
```

### Scroll Operations

```python
# Scroll to an element using JavaScript
selixir.scroll_to_element_by_js(driver, element)

# Robust scrolling combining various methods
selixir.scroll_to_target(driver, element_or_xpath)
```

### File Operations

```python
# Get the latest file in a directory
latest_file = selixir.get_latest_file_path(download_dir)

# Wait for a new file to be created
new_file = selixir.wait_for_new_file(download_dir, timeout_seconds=60)
```

## Contributing

Issues and pull requests are welcome on the GitHub repository.
