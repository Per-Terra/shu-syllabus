import argparse
import json
import os
from typing import Any


def main(nendo: str) -> None:
    directory = os.path.join(os.path.dirname(__file__), f"syllabus/{nendo}")
    json_data: list[Any] = []

    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            file_path = os.path.join(directory, filename)

            with open(file_path, "r") as file:
                json_content = json.load(file)

            json_data.append(json_content)

    file_path = os.path.join(
        os.path.dirname(__file__), f"../src/shu_syllabus/data/syllabus/{nendo}.json"
    )

    with open(file_path, "w") as file:
        json.dump(json_data, file, ensure_ascii=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bundle syllabus data.")
    parser.add_argument(
        "nendo", type=str, help="Academic year of the syllabus data to bundle."
    )
    args = parser.parse_args()
    main(args.nendo)
