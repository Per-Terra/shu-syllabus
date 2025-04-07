import argparse
import json
import os
import sys
from time import sleep

import requests

sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from shu_syllabus import SyllabusData, SyllabusSearch

SLEEP_SECONDS = 0.5  # Number of seconds to sleep to avoid server overload


def main(nendo: str) -> None:
    directory = os.path.join(os.path.dirname(__file__), f"syllabus/{nendo}")
    if not os.path.exists(directory):
        os.makedirs(directory)

    with requests.Session() as session:
        # シラバスのコードを取得
        syllabus_codes = SyllabusSearch(nendo, session=session).parse()
        # 不要なファイルを削除
        valid_files = {f"{code[2]}.json" for code in syllabus_codes}
        for filename in os.listdir(directory):
            if filename.endswith(".json") and filename not in valid_files:
                file_to_delete = os.path.join(directory, filename)
                print(f"Deleting obsolete file: {filename}")
                os.remove(file_to_delete)
        # シラバスデータを取得
        for i, syllabus_code in enumerate(syllabus_codes):
            print(f"Fetching {i + 1}: {syllabus_code} ", end="")
            syllabus = SyllabusData(*syllabus_code, session=session)
            file_path = os.path.join(directory, f"{syllabus_code[2]}.json")
            new_data = syllabus.parse()
            new_data.pop("_fetched_at", None)
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    old_data = json.load(f)
                old_data.pop("_fetched_at", None)
                if old_data == new_data:
                    print(f"No changes for {syllabus_code[2]}, skipping save.")
                    sleep(SLEEP_SECONDS)
                    continue
            print(f"Saving {syllabus_code[2]} to {file_path}")
            syllabus.save_as_json(file_path)
            sleep(SLEEP_SECONDS)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch and save syllabus data.")
    parser.add_argument(
        "nendo", type=str, help="Academic year of the syllabus data to fetch."
    )
    args = parser.parse_args()
    main(args.nendo)
