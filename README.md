# shu-syllabus

周南公立大学の [Active Academy Advance (AAA)](https://aaaweb.shunan-u.ac.jp/aa_web/syllabus/se0010.aspx?me=EU&opi=mt0010) からシラバスデータをスクレイピング・ロードする Python ライブラリ。2023年度以降のシラバスデータを同梱しており、インストールすればすぐに使えます。

周南公立大学の2024年度開講科目「Python応用」の最終課題として作成しました。提出時点のコードは [v0.1.0](https://github.com/Per-Terra/shu-syllabus/releases/tag/v0.1.0) を参照してください。v1.0.0 で API を全面的に見直し、型安全なデータモデルを導入しています。

## インストール

```shell
pip install git+https://github.com/Per-Terra/shu-syllabus.git
```

## 使い方

### バンドル済みデータの読み込み

```python
import shu_syllabus

syllabuses = shu_syllabus.load("2025")  # list[Syllabus]

s = syllabuses[0]
s.name_ja           # '意思決定科学'
s.credits           # 2
s.teachers          # [Teacher(name='喜入　暁', is_primary=False)]
s.evaluation_ratio  # EvaluationRatio(exam=0, quiz=0, report=70, ...)
```

### 絞り込み

```python
# Python の標準的なリスト操作で絞り込む
python_courses = [s for s in syllabuses if "Python" in (s.name_ja or "")]
first_year = [s for s in syllabuses if s.target_year == 1]
```

### AAAサーバーからの直接取得

```python
with shu_syllabus.Scraper() as scraper:
    codes = scraper.search("2025")                  # list[str]
    syllabus = scraper.fetch("2025", codes[0])      # Syllabus
```

## データモデル

すべてのフィールドを dataclass で定義しており、IDE の補完・型チェックが利きます。各フィールドの docstring には元の日本語項目名を記載しています。

- `Syllabus` — シラバス本体（30+フィールド）
- `Teacher` — 担当教員（name, is_primary）
- `Book` — 教科書・参考図書
- `ScheduleEntry` — 授業計画の各回
- `EvaluationRatio` — 評価比率（exam, quiz, report, presentation, portfolio, other）
- `EnrollmentInfo` — 履修上の注意（prerequisites, recommended, required_materials, other）

## データ更新

```shell
# AAAサーバーから取得
shu-syllabus-update 2025

# パッケージ用にバンドル
shu-syllabus-bundle 2025
```

GitHub Actions で毎週自動チェックし、変更があれば PR を作成します。

## 開発

```shell
pip install -e ".[dev]"
pytest
```

## ライセンス

[LICENSE](LICENSE) を参照してください（シラバスデータを除く）。
