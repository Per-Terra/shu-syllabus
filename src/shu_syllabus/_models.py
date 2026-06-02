from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class Teacher:
    """担当教員情報。

    Attributes:
        name: 教員名
        is_primary: 主担当かどうか（「（主）」表記に対応）
    """

    name: str
    is_primary: bool = False


@dataclass(frozen=True)
class Book:
    """教科書・参考図書。

    Attributes:
        title: 書籍名
        publication_year: 発行年（西暦）
        author: 著作者名
        publisher: 出版社
        price: 金額（税込、円）
        isbn: ISBN
        available_on_campus: 学内販売の有無
    """

    title: str
    publication_year: int | None = None
    author: str | None = None
    publisher: str | None = None
    price: int | None = None
    isbn: str | None = None
    available_on_campus: bool = False


@dataclass(frozen=True)
class ScheduleEntry:
    """授業計画の各回。

    Attributes:
        number: 回数
        content: 授業内容
        teaching_methods: 授業方法（講義・演習等）
        teachers: 担当教員
    """

    number: str
    content: str | None = None
    teaching_methods: list[str] = field(default_factory=list)
    teachers: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class EvaluationRatio:
    """学生に対する評価の比率（%）。

    Attributes:
        exam: 試験
        quiz: 小テスト
        report: レポート
        presentation: 発表・実技
        portfolio: ポートフォリオ
        other: その他
    """

    exam: int = 0
    quiz: int = 0
    report: int = 0
    presentation: int = 0
    portfolio: int = 0
    other: int = 0


@dataclass(frozen=True)
class TeachingCertificate:
    """教職関連

    Attributes:
        subject: 大区分
        enforcement: 免許法施行規則に定める科目区分
    """

    subject: str | None = None
    enforcement: str | None = None


@dataclass(frozen=True)
class EnrollmentInfo:
    """履修上の注意。

    Attributes:
        prerequisites: 先修条件科目（必須）
        recommended: 先修条件科目（推奨）
        required_materials: 持参物
        other: その他
    """

    prerequisites: list[str] = field(default_factory=list)
    recommended: list[str] = field(default_factory=list)
    required_materials: str | None = None
    other: str | None = None


@dataclass
class Syllabus:
    """シラバスデータ。

    Attributes:
        fetched_at: データ取得日時（ISO 8601）
        name_ja: 授業科目名称
        name_en: 英文科目名称
        syllabus_number: シラバス番号
        course_number: 科目ナンバー
        departments: 対象学科・コース
        category: 専門・総合・教職
        home_department: 主学科
        requirements: 要件
        target_year: 配当年
        time_slot: 時限
        required_or_elective: 必選
        course_division: 科目区分
        instruction_format: 担当形態（単独・複数・オムニバス等）
        teachers: 担当教員
        term: 開講期間
        credits: 単位数
        teaching_methods: 授業方法（講義・演習・実験等）
        delivery_modes: 授業形態（対面・オンライン等）
        objectives: 授業のテーマ及び到達目標
        overview: 授業の概要
        diploma_policies: 対応するディプロマ・ポリシー
        textbooks: 教科書
        references: 参考図書
        enrollment_info: 履修上の注意
        teaching_certificate: 教職関連
        grading_criteria: 評価基準
        evaluation_ratio: 学生に対する評価（比率）
        teacher_message: 担当教員からのメッセージ
        schedule: 授業計画と学習課題
        credit_auditing: 科目等履修制度
        practitioner_info: 実務家教員担当科目に関する記載
    """

    fetched_at: str | None = None
    name_ja: str | None = None
    name_en: str | None = None
    syllabus_number: str | None = None
    course_number: str | None = None
    departments: list[str] = field(default_factory=list)
    category: str | None = None
    home_department: str | None = None
    requirements: str | None = None
    target_year: int | None = None
    time_slot: str | None = None
    required_or_elective: str | None = None
    course_division: str | None = None
    instruction_format: str | None = None
    teachers: list[Teacher] = field(default_factory=list)
    term: str | None = None
    credits: int | None = None
    teaching_methods: list[str] = field(default_factory=list)
    delivery_modes: list[str] = field(default_factory=list)
    objectives: str | None = None
    overview: str | None = None
    diploma_policies: list[str] = field(default_factory=list)
    textbooks: list[Book] = field(default_factory=list)
    references: list[Book] = field(default_factory=list)
    enrollment_info: EnrollmentInfo = field(default_factory=EnrollmentInfo)
    teaching_certificate: TeachingCertificate | None = None
    grading_criteria: str | None = None
    evaluation_ratio: EvaluationRatio = field(default_factory=EvaluationRatio)
    teacher_message: str | None = None
    schedule: list[ScheduleEntry] = field(default_factory=list)
    credit_auditing: bool | None = None
    practitioner_info: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """dict に変換する。JSON シリアライズ可能。"""
        return asdict(self)
