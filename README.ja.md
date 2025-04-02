# Selixir

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

# デバッグモードを有効化するとログが表示される
selixir.debug(True)

# ChromeDriverを起動
driver = selixir.driver_start("https://example.com")

# 要素までスクロール
element = driver.find_element(By.ID, "target-element")
selixir.scroll_to_target(driver, element)

# 新しいタブでリンクを開く
link_element = driver.find_element(By.XPATH, "//a[contains(text(), 'リンク')]")
if selixir.switch_to_new_tab(driver, link_element):
    print("新しいタブに切り替わりました")

# ダウンロードディレクトリの最新ファイルを取得
download_dir = "/path/to/downloads"
latest_file = selixir.get_latest_file_path(download_dir)
```

## 主な機能

### ログ出力のカスタマイズ

```python
# デバッグモードを有効にするとログが標準出力に表示される
selixir.debug(True)  # 有効化
selixir.debug(False) # 無効化

# 独自のロガー設定を行う場合は以下のように設定可能
import logging

# ロガーの取得
selixir_logger = logging.getLogger("selixir")

# 独自のログハンドラーを設定
file_handler = logging.FileHandler("selixir.log")
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
selixir_logger.addHandler(file_handler)
selixir_logger.setLevel(logging.DEBUG)  # ログレベルを設定
```

### ドライバー管理

```python
# ドライバー操作中にログを表示する
selixir.debug(True)

# ドライバーを起動
driver = selixir.driver_start(url)

# Heroku環境用の設定でドライバー起動
driver = selixir.driver_start(url, heroku_mode=True)
```

### タブ操作

```python
# 新しいタブを開く
selixir.open_new_tab(driver, "https://example.com")

# 現在のタブ以外をすべて閉じる
selixir.close_other_tabs(driver)

# Control+クリックでリンクを新しいタブで開く
element = driver.find_element(By.XPATH, "//a[@href='https://example.com']")
selixir.perform_control_click(driver, element)

# Control+クリックして新規タブに切り替え
success = selixir.switch_to_new_tab(driver, element)
if success:
    print('新しいタブに切り替わりました')
```

### スクロール操作

```python
# JavaScriptを使用して要素へスクロール
selixir.scroll_to_element_by_js(driver, element)

# 様々な方法を組み合わせた堅牢なスクロール
selixir.scroll_to_target(driver, element_or_xpath)
```

### ファイル操作

```python
# ディレクトリ内の最新ファイルを取得
latest_file = selixir.get_latest_file_path(download_dir)

# 新しいファイルが作成されるのを待つ
new_file = selixir.wait_for_new_file(download_dir, timeout_seconds=60)

# ダウンロード開始前のファイル一覧を使ってダウンロード完了を追跡
before_files = set(os.listdir(download_dir))
# ここでダウンロード操作を行います...
completed_file = selixir.wait_for_download_completion(download_dir, before_files, timeout=60)
```

## 貢献

問題の報告やプルリクエストは GitHub リポジトリで受け付けています。
