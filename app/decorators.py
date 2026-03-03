from functools import wraps
from flask import abort
from flask_login import current_user
from .models import Course, Enrollment, GroupMember

def role_required(*roles):
    def deco(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.role not in roles:
                abort(403)
            return fn(*args, **kwargs)
        return wrapper
    return deco

def teacher_owns_course(course_id: int) -> bool:
    c = Course.query.get(course_id)
    return bool(c and c.teacher_id == current_user.id)

def student_enrolled(course_id: int) -> bool:
    return Enrollment.query.filter_by(course_id=course_id, user_id=current_user.id).first() is not None

def require_course_access(course_id: int):
    if current_user.role == "TEACHER":
        if not teacher_owns_course(course_id):
            abort(403)
    else:
        if not student_enrolled(course_id):
            abort(403)

def require_student_in_group(group_id: int):
    if current_user.role == "TEACHER":
        return
    is_member = GroupMember.query.filter_by(group_id=group_id, user_id=current_user.id).first()
    if not is_member:
        abort(403)
