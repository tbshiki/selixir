# selixir

SelixirはSelenium WebDriverを使いやすくするための軽量ラッパーライブラリです。
ブラウザの自動操作をより簡単かつ堅牢にするための便利なユーティリティ関数を提供します。

## 機能

- **ドライバー管理**: ChromeDriverの起動と設定を簡単に行えます
- **クリック操作制御**: 新しいタブでのリンクオープンやタブの管理を行えます
- **スクロール操作**: 様々な方法で要素までスクロールできます
- **ファイル操作**: ダウンロードファイルの監視などに便利な関数を提供しています

## 簡単な使い方

```python
import selixir
from selenium.webdriver.common.by import By

# ChromeDriverを起動
driver = selixir.driver_start("https://example.com")

# 要素までスクロール
element = driver.find_element(By.ID, "target-element")
selixir.scroll_to_target(driver, element)

# 新しいタブでリンクを開く
link_element = driver.find_element(By.XPATH, "//a[contains(text(), 'リンク')]")
selixir.ClickControl.switch_to_new_tab(driver, link_element)

# ダウンロードディレクトリの最新ファイルを取得
download_dir = "/path/to/downloads"
latest_file = selixir.get_latest_file_path(download_dir)
```

## 主な機能

### ドライバー管理

```python
# 基本的なドライバー起動
driver = selixir.driver_start(url)

# Heroku環境用の設定でドライバー起動
driver = selixir.driver_start(url, heroku_mode=True)

# ロガーを指定してドライバー起動
driver = selixir.driver_start(url, logger=my_logger)
```

### タブ操作

```python
# 新しいタブを開く
selixir.open_new_tab(driver, "https://example.com")

# 現在のタブ以外をすべて閉じる
selixir.close_other_tabs(driver)
```

### スクロール操作

```python
# JavaScriptを使用して要素へスクロール
selixir.scroll_to_element_by_js(driver, element)

# 推奨: 様々な方法を組み合わせた堅牢なスクロール
selixir.scroll_to_target(driver, element_or_xpath)
```

### ファイル操作

```python
# ディレクトリ内の最新ファイルを取得
latest_file = selixir.get_latest_file_path(download_dir)

# 新しいファイルが作成されるのを待つ
new_file = selixir.wait_for_new_file(download_dir, timeout_seconds=60)
```

## 貢献

問題の報告やプルリクエストは GitHub リポジトリで受け付けています。
