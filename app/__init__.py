import os
from pathlib import Path

import click
from dotenv import load_dotenv
from flask import Flask, render_template
from flask_login import login_required

from .config import Config
from .extensions import db, migrate, login_manager, csrf
from .models import User


def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(app.config["UPLOAD_DIR"], exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    @login_manager.user_loader
    def load_user(user_id: str):
        return User.query.get(int(user_id))

    # Blueprints
    from .auth import bp as auth_bp
    from .courses import bp as courses_bp
    from .groups import bp as groups_bp
    from .assignments import bp as assignments_bp
    from .submissions import bp as submissions_bp
    from .grading import bp as grading_bp
    from .exports import bp as exports_bp
    from .files import bp as files_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(groups_bp)
    app.register_blueprint(assignments_bp)
    app.register_blueprint(submissions_bp)
    app.register_blueprint(grading_bp)
    app.register_blueprint(exports_bp)
    app.register_blueprint(files_bp)

    @app.get("/")
    @login_required
    def dashboard():
        return render_template("dashboard.html")

    # CLI: seed users from Excel (không dùng route /auth/seed nữa)
    @app.cli.command("seed-users")
    @click.option("--teacher", "teacher_path", default="seed_data/teacher.xlsx", show_default=True, help="Excel tài khoản giáo viên")
    @click.option("--students", "students_path", default="seed_data/students_70.xlsx", show_default=True, help="Excel tài khoản học sinh")
    @click.option("--no-students", is_flag=True, help="Chỉ seed GV (bỏ seed HS)")
    def seed_users_cmd(teacher_path: str, students_path: str, no_students: bool):
        """Seed user accounts from Excel files into DB (idempotent)."""
        from .utils.seed_excel import seed_users_from_excel

        base_dir = Path(app.root_path).parent

        def resolve(p: str) -> str:
            if os.path.isabs(p):
                return p
            return str((base_dir / p).resolve())

        teacher_abs = resolve(teacher_path)
        students_abs = None if no_students else resolve(students_path)

        if not os.path.exists(teacher_abs):
            raise click.ClickException(f"Không tìm thấy file teacher: {teacher_abs}")
        if students_abs and not os.path.exists(students_abs):
            raise click.ClickException(f"Không tìm thấy file students: {students_abs}")

        with app.app_context():
            result = seed_users_from_excel(teacher_abs, students_abs)

        click.echo(
            f"Seed OK. created={result['created']}, updated_name={result['updated_name']}, existed_skipped={result['skipped']}"
        )

    return app
