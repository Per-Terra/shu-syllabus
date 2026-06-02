"""既存JSONデータのキー名を v2 形式に移行するスクリプト。"""

from __future__ import annotations

import argparse
import json
import os
from typing import Any

_TOP_KEY_MAP = {
    "_fetched_at": "fetched_at",
    "target_departments_and_courses": "departments",
    "type": "category",
    "main_department": "home_department",
    "year": "target_year",
    "period": "time_slot",
    "course_category": "course_division",
    "class_type": "instruction_format",
    "class_forms": "delivery_modes",
    "themes_and_goals": "objectives",
    "corresponding_diploma_policies": "diploma_policies",
    "reference_books": "references",
    "notes_on_enrollment": "enrollment_info",
    "evaluation_criteria": "grading_criteria",
    "message_from_teachers": "teacher_message",
    "open_to_non_students": "credit_auditing",
    "practitioner": "practitioner_info",
}

_TEACHER_KEY_MAP = {"main": "is_primary"}

_BOOK_KEY_MAP = {"year": "publication_year"}

_ENROLLMENT_KEY_MAP = {
    "required_courses": "prerequisites",
    "recommended_courses": "recommended",
    "brings": "required_materials",
}

_EVAL_KEY_MAP = {
    "試験": "exam",
    "小テスト": "quiz",
    "レポート": "report",
    "発表・実技": "presentation",
    "ポートフォリオ": "portfolio",
    "その他": "other",
}

_SCHEDULE_KEY_MAP = {
    "session": "number",
    "methods": "teaching_methods",
}


def _rename_keys(d: dict[str, Any], key_map: dict[str, str]) -> dict[str, Any]:
    return {key_map.get(k, k): v for k, v in d.items()}


def migrate_syllabus(data: dict[str, Any]) -> dict[str, Any]:
    """1件のシラバスデータを v2 キー名に変換する。"""
    result = _rename_keys(data, _TOP_KEY_MAP)

    if "teachers" in result and isinstance(result["teachers"], list):
        result["teachers"] = [
            _rename_keys(t, _TEACHER_KEY_MAP) for t in result["teachers"]
        ]

    for book_field in ("textbooks", "references"):
        if book_field in result and isinstance(result[book_field], list):
            result[book_field] = [
                _rename_keys(b, _BOOK_KEY_MAP) for b in result[book_field]
            ]

    if "enrollment_info" in result and isinstance(result["enrollment_info"], dict):
        result["enrollment_info"] = _rename_keys(
            result["enrollment_info"], _ENROLLMENT_KEY_MAP
        )

    if "evaluation_ratio" in result and isinstance(result["evaluation_ratio"], dict):
        result["evaluation_ratio"] = _rename_keys(
            result["evaluation_ratio"], _EVAL_KEY_MAP
        )

    if "schedule" in result and isinstance(result["schedule"], list):
        result["schedule"] = [
            _rename_keys(s, _SCHEDULE_KEY_MAP) for s in result["schedule"]
        ]

    return result


def _is_already_migrated(data: dict[str, Any]) -> bool:
    """v2 キーがすでに存在するかチェック。"""
    return "fetched_at" in data or "departments" in data or "category" in data


def migrate_file(path: str) -> bool:
    """JSONファイルを移行する。変更があった場合 True を返す。"""
    with open(path) as f:
        data = json.load(f)

    if isinstance(data, list):
        if not data or _is_already_migrated(data[0]):
            return False
        data = [migrate_syllabus(d) for d in data]
    elif isinstance(data, dict):
        if _is_already_migrated(data):
            return False
        data = migrate_syllabus(data)
    else:
        return False

    with open(path, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        f.write("\n")

    return True


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Migrate syllabus JSON to v2 key names."
    )
    parser.add_argument("nendo", help="Academic year (e.g., 2025)")
    args = parser.parse_args()
    nendo = args.nendo

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "..", "..", ".."))

    individual_dir = os.path.join(project_root, "data", "syllabus", nendo)
    if os.path.isdir(individual_dir):
        count = 0
        for filename in sorted(os.listdir(individual_dir)):
            if filename.endswith(".json"):
                path = os.path.join(individual_dir, filename)
                if migrate_file(path):
                    count += 1
        print(f"Migrated {count} individual files in {individual_dir}")

    bundled_path = os.path.join(
        project_root, "src", "shu_syllabus", "data", "syllabus", f"{nendo}.json"
    )
    if os.path.isfile(bundled_path):
        if migrate_file(bundled_path):
            print(f"Migrated bundled file: {bundled_path}")
        else:
            print(f"Bundled file already migrated: {bundled_path}")


if __name__ == "__main__":
    main()
