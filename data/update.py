import argparse
import os
import sys
from time import sleep

import requests

sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from shu_syllabus import SyllabusData, SyllabusSearch


def main(nendo: str) -> None:
    directory = os.path.join(os.path.dirname(__file__), f"syllabus/{nendo}")
    if not os.path.exists(directory):
        os.makedirs(directory)

    with requests.Session() as session:
        syllabus_codes = SyllabusSearch(nendo, session=session).parse()
        for i, syllabus_code in enumerate(syllabus_codes):
            print(f"Fetching {i + 1}: {syllabus_code}")
            syllabus = SyllabusData(*syllabus_code, session=session)
            syllabus.save_as_json(os.path.join(directory, f"{syllabus_code[2]}.json"))
            sleep(2)  # Sleep for 2 second to avoid overloading the server


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch and save syllabus data.")
    parser.add_argument(
        "nendo", type=str, help="Academic year of the syllabus data to fetch."
    )
    args = parser.parse_args()
    main(args.nendo)
