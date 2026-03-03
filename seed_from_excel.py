"""One-click seeding users from Excel (teacher + 70 students).

Usage (after `flask db upgrade`):
  python seed_from_excel.py

Or use Flask CLI:
  python -m flask --app run.py seed-users
"""

import os
from pathlib import Path

from app import create_app


def main():
    app = create_app()
    base_dir = Path(__file__).resolve().parent

    teacher = base_dir / "seed_data" / "teacher.xlsx"
    students = base_dir / "seed_data" / "students_70.xlsx"

    if not teacher.exists():
        raise SystemExit(f"Missing: {teacher}")

    from app.utils.seed_excel import seed_users_from_excel

    with app.app_context():
        res = seed_users_from_excel(str(teacher), str(students) if students.exists() else None)

    print(f"Seed OK: {res}")


if __name__ == "__main__":
    main()
