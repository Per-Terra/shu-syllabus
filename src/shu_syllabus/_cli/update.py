"""AAAサーバーからシラバスデータを取得して個別JSONファイルとして保存する。"""

from __future__ import annotations

import argparse
import json
import os
from time import sleep

from .._scraper import Scraper


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch syllabus data from AAA.")
    parser.add_argument("nendo", help="Academic year (e.g., 2025)")
    parser.add_argument(
        "--delay",
        type=float,
        default=0.5,
        help="Seconds between requests (default: 0.5)",
    )
    parser.add_argument(
        "--data-dir",
        default=None,
        help="Output directory (default: data/syllabus/<nendo>)",
    )
    args = parser.parse_args()
    nendo: str = args.nendo
    delay: float = args.delay

    if args.data_dir:
        directory = args.data_dir
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(script_dir, "..", "..", ".."))
        directory = os.path.join(project_root, "data", "syllabus", nendo)

    os.makedirs(directory, exist_ok=True)

    with Scraper() as scraper:
        print(f"Searching syllabuses for {nendo}...")
        codes = scraper.search(nendo)
        print(f"Found {len(codes)} syllabuses.")

        valid_files = {f"{code}.json" for code in codes}
        for filename in os.listdir(directory):
            if filename.endswith(".json") and filename not in valid_files:
                path = os.path.join(directory, filename)
                print(f"Deleting obsolete file: {filename}")
                os.remove(path)

        for i, syllabus_no in enumerate(codes):
            print(f"Fetching {i + 1}/{len(codes)}: {syllabus_no} ", end="")
            syllabus = scraper.fetch(nendo, syllabus_no)
            file_path = os.path.join(directory, f"{syllabus_no}.json")

            new_data = syllabus.to_dict()
            new_data.pop("fetched_at", None)

            if os.path.exists(file_path):
                with open(file_path) as f:
                    old_data = json.load(f)
                old_data.pop("fetched_at", None)
                if old_data == new_data:
                    print("(no changes)")
                    sleep(delay)
                    continue

            print("(saving)")
            with open(file_path, "w") as f:
                json.dump(syllabus.to_dict(), f, ensure_ascii=False, indent=4)
                f.write("\n")
            sleep(delay)


if __name__ == "__main__":
    main()
