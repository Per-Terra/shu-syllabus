# shu-syllabus

A collection of datasets and utility scripts for managing and analyzing Shunan University syllabuses.

## Overview

### English

This library was created as the final project for the 2024 course “Applied Python Programming” at Shunan University. The syllabus data is based on [Shunan University](https://www.shunan-u.ac.jp/) and its [Active Academy Advance (AAA)](https://aaaweb.shunan-u.ac.jp/aa_web/syllabus/se0010.aspx?me=EU&opi=mt0010) system. The library includes pre-processed syllabus data, allowing you to start analysis immediately.

### 日本語

このライブラリは周南公立大学の2024年度開講科目「Python応用」の最終課題として作成されました。シラバスデータは[周南公立大学](https://www.shunan-u.ac.jp/)の[Active Academy Advance (AAA)](https://aaaweb.shunan-u.ac.jp/aa_web/syllabus/se0010.aspx?me=EU&opi=mt0010)に基づきます。このライブラリには事前に取得されたシラバスデータが含まれているため、すぐに分析を始めることができます。

## Features

- Pre-processed syllabus data (only for data from 2023 onwards)
- Fetch syllabus data from Shunan University's Active Academy Advance (AAA) system
- Parse syllabus data (only for data from 2023 onwards)
- Save syllabus data as a JSON file

## Usage

### Install

```shell
pip install git+https://github.com/Per-Terra/shu-syllabus.git
```

### Load syllabuses

You can load pre-processed syllabus data using the `load_syllabuses` function.

```python
>>> from shu_syllabus import load_syllabuses
>>> syllabuses = load_syllabuses("2024")
>>> type(syllabuses)
list
>>> syllabus = syllabuses[0]
>>> type(syllabus)
dict
>>> syllabus["name_ja"]
'問題発見と解決'
```

### Search syllabuses

You can search for syllabuses by keyword like this.

```python
>>> from shu_syllabus import load_syllabuses
>>> syllabuses = load_syllabuses("2024")
>>> results = [s for s in syllabuses if "Python" in s["name_ja"]]
>>> len(results)
3
>>> results[2]["name_ja"]
'Python応用'
```

## Advanced Usage

If you don't want to use the pre-processed data, you can use the following functions to fetch and process the syllabus data.

### Fetch syllabuses list

You can fetch the list of syllabuses from Shunan University's Active Academy Advance (AAA) system using the `SyllabusSearch` class.

```python
>>> from shu_syllabus import SyllabusSearch
>>> syllabuses_list = SyllabusSearch("2024").parse()
>>> type(syllabuses_list)
list
>>> syllabus_code = syllabuses_list[0]
>>> type(syllabus_code)
tuple
>>> syllabus_code
('2024', '2', '1000500A')
```

### Fetch syllabus details

You can fetch the details of a syllabus from Shunan University's Active Academy Advance (AAA) system using the `SyllabusData` class.

```python
>>> from shu_syllabus import SyllabusData, SyllabusSearch
>>> syllabuses_list = SyllabusSearch("2024").parse()
>>> syllabus_code = syllabuses_list[0]
>>> syllabus_data = SyllabusData(*syllabus_code)
>>> syllabus = syllabus_data.parse()
>>> type(syllabus)
dict
>>> syllabus["name_ja"]
'問題発見と解決'
```

### Save syllabus data

You can save the syllabus data as a JSON file using the `save_as_json` method.

```python
>>> from shu_syllabus import SyllabusData, SyllabusSearch
>>> syllabuses_list = SyllabusSearch("2024").parse()
>>> syllabus_code = syllabuses_list[0]
>>> syllabus_data = SyllabusData(*syllabus_code)
>>> syllabus_data.save_as_json("syllabus.json")
```

## Build

Before you build, you should update the syllabus data.

> [!NOTE]
> To avoid overloading the server, it takes a long time to fetch the syllabus data (about 20 minutes). Please be patient.

```shell
python data/update.py 2024
```

Then, you should bundle the syllabus data. Bundled data is included in the package.

```shell
python data/bundle.py 2024
```

Finally, you can build the package.

```shell
python -m build
```

## License

See [LICENSE](LICENSE), except for the syllabus data.
