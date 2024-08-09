import argparse
import json
import os
from typing import Any


def main(nendo: str) -> None:
    directory = os.path.join(os.path.dirname(__file__), f"syllabus/{nendo}")
    syllabuses: list[Any] = []

    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            file_path = os.path.join(directory, filename)

            with open(file_path, "r") as file:
                syllabus_data = json.load(file)

            syllabuses.append(syllabus_data)

    syllabuses.sort(key=lambda syllabus: syllabus["syllabus_number"])

    file_path = os.path.join(
        os.path.dirname(__file__), f"../src/shu_syllabus/data/syllabus/{nendo}.json"
    )

    with open(file_path, "w") as file:
        json.dump(syllabuses, file, ensure_ascii=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bundle syllabus data.")
    parser.add_argument(
        "nendo", type=str, help="Academic year of the syllabus data to bundle."
    )
    args = parser.parse_args()
    main(args.nendo)
