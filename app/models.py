from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db

class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(190), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # TEACHER | STUDENT
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, pw: str):
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw: str) -> bool:
        return check_password_hash(self.password_hash, pw)

class Course(db.Model):
    __tablename__ = "courses"
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    # Group constraints (0 = unlimited)
    max_group_size = db.Column(db.Integer, nullable=False, default=5)
    max_groups = db.Column(db.Integer, nullable=False, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Enrollment(db.Model):
    __tablename__ = "enrollments"
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Group(db.Model):
    __tablename__ = "groups"
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    leader_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class GroupMember(db.Model):
    __tablename__ = "group_members"
    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Assignment(db.Model):
    __tablename__ = "assignments"
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    deadline_at = db.Column(db.DateTime, nullable=False)
    rubric_json = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Submission(db.Model):
    __tablename__ = "submissions"
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey("assignments.id"), nullable=False, index=True)
    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"), nullable=False, index=True)
    submitted_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    link_url = db.Column(db.String(500), nullable=True)
    note = db.Column(db.Text, nullable=True)

class SubmissionFile(db.Model):
    __tablename__ = "submission_files"
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey("submissions.id"), nullable=False, index=True)
    file_path = db.Column(db.String(500), nullable=False)   # relative path under UPLOAD_DIR
    original_name = db.Column(db.String(255), nullable=False)
    size = db.Column(db.Integer, nullable=True)

class Grade(db.Model):
    __tablename__ = "grades"
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey("submissions.id"), unique=True, nullable=False, index=True)
    score = db.Column(db.Float, nullable=True)
    feedback = db.Column(db.Text, nullable=True)
    graded_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    graded_at = db.Column(db.DateTime, default=datetime.utcnow)
    return_file_path = db.Column(db.String(500), nullable=True)

class AuditLog(db.Model):
    __tablename__ = "audit_logs"
    id = db.Column(db.Integer, primary_key=True)
    actor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    action = db.Column(db.String(120), nullable=False)
    entity_type = db.Column(db.String(80), nullable=True)
    entity_id = db.Column(db.Integer, nullable=True)
    meta_json = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
