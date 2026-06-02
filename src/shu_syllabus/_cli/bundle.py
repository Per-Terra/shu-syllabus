"""個別JSONファイルをパッケージ用に1ファイルにバンドルする。"""

from __future__ import annotations

import argparse
import json
import os

from .._utils import letter_to_number


def main() -> None:
    parser = argparse.ArgumentParser(description="Bundle individual syllabus JSONs.")
    parser.add_argument("nendo", help="Academic year (e.g., 2025)")
    args = parser.parse_args()
    nendo: str = args.nendo

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "..", "..", ".."))
    individual_dir = os.path.join(project_root, "data", "syllabus", nendo)
    output_path = os.path.join(
        project_root, "src", "shu_syllabus", "data", "syllabus", f"{nendo}.json"
    )

    syllabuses: list[dict] = []
    for filename in os.listdir(individual_dir):
        if filename.endswith(".json"):
            with open(os.path.join(individual_dir, filename)) as f:
                syllabuses.append(json.load(f))

    syllabuses.sort(
        key=lambda s: (
            int(s["syllabus_number"][:7]),
            letter_to_number(s["syllabus_number"][7:]),
        )
    )

    with open(output_path, "w") as f:
        json.dump(syllabuses, f, ensure_ascii=False)

    print(f"Bundled {len(syllabuses)} syllabuses to {output_path}")


if __name__ == "__main__":
    main()
