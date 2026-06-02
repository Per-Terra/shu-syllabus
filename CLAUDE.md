# CLAUDE.md

このファイルは、Claude Code (claude.ai/code) がこのリポジトリで作業する際のガイドです。

## プロジェクト概要

周南公立大学の Active Academy Advance (AAA) システムからシラバスデータをスクレイピング・パース・バンドルするPythonライブラリ。事前取得済みのシラバスデータ（2023年度以降）を同梱しており、`shu_syllabus.load("2025")` ですぐに分析を開始できる。AAAシステムはASP.NET WebFormsアプリケーションのため、スクレイピングにはViewStateや隠しフィールドの管理が必要。

## コマンド

```shell
# 開発モードでインストール
pip install -e ".[dev]"

# テスト実行
pytest

# AAAサーバーからシラバスデータを更新（約20分、リクエスト間隔0.5秒）
shu-syllabus-update <年度>    # 例: shu-syllabus-update 2025

# 個別JSONファイルをパッケージ用に1ファイルにバンドル
shu-syllabus-bundle <年度>    # 例: shu-syllabus-bundle 2025

# パッケージをビルド
python -m build
```

## アーキテクチャ

**ローディング**（バンドル済みJSONの読み込み）と**スクレイピング**（AAAから取得）の2つのデータパスがある。

### Public API

```python
import shu_syllabus

# バンドル済みデータの読み込み
syllabuses = shu_syllabus.load("2025")    # list[Syllabus]

# ライブ取得
with shu_syllabus.Scraper() as scraper:
    codes = scraper.search("2025")         # list[str]
    syllabus = scraper.fetch("2025", codes[0])  # Syllabus
```

### パッケージ構造

```
src/shu_syllabus/
    __init__.py      # Public API: load, Scraper, 全dataclass
    _models.py       # dataclass定義（Syllabus, Teacher, Book 等）
    _loader.py       # load() — importlib.resourcesでバンドルJSON読み込み
    _parser.py       # HTML→Syllabus パース（純粋関数、I/Oなし）
    _scraper.py      # Scraper クラス（ネットワークI/O）
    _aspnet.py       # ASP.NET ViewState抽出
    _urls.py         # URL定数
    _utils.py        # make_soup, letter_to_number 等
    _cli/            # CLIエントリポイント（update, bundle, migrate）
    data/syllabus/   # バンドル済みJSON（2023-2025）
```

### 設計原則

- `_parser.py` はI/Oなしの純粋関数。HTMLを受け取り `Syllabus` を返す。テスト容易性が最も高い
- `_scraper.py` はネットワークI/Oのみ。パースは `_parser.py` に委譲
- `_models.py` のネストした値オブジェクト（Teacher, Book等）は `frozen=True`
- 空文字列はロード/パース時に `None` に正規化

### 主要な規約

- `nendo` = 年度。常に文字列（例: "2024"）
- `syllabusNo` = 7桁数字 + アルファベット接尾辞（例: "1000500A"）。アルファベット部分はExcelの列番号方式で増分（A-Z, AA-AZ, BA...）
- 2023年度以降のデータのみ対応（パース形式が変更されたため）
- Python >=3.10 が必要（PEP 604 のユニオン型構文 `X | Y` を使用）
- アンダースコア接頭辞のモジュール（`_models.py` 等）は内部モジュール。`__init__.py` 経由でのみ公開
