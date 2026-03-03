from flask import render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from . import bp
from .forms import AssignmentForm
from ..decorators import role_required, require_course_access
from ..extensions import db
from ..models import Course, Assignment, Group, GroupMember
from ..audit import log_action


@bp.get("")
@login_required
def list_assignments():
    course_id = request.args.get("course_id", type=int)
    if not course_id:
        flash("Thiếu course_id", "warning")
        return redirect(url_for("courses.list_courses"))

    require_course_access(course_id)
    items = Assignment.query.filter_by(course_id=course_id).order_by(Assignment.created_at.desc()).all()
    course = Course.query.get_or_404(course_id)
    return render_template("assignments/list.html", assignments=items, course=course)


@bp.get("/create")
@login_required
@role_required("TEACHER")
def create_assignment():
    course_id = request.args.get("course_id", type=int)
    if not course_id:
        abort(400)
    c = Course.query.get_or_404(course_id)
    if c.teacher_id != current_user.id:
        abort(403)

    form = AssignmentForm()
    form.course_id.data = course_id
    return render_template("assignments/create_edit.html", form=form, mode="create")


@bp.post("/create")
@login_required
@role_required("TEACHER")
def create_assignment_post():
    form = AssignmentForm()
    if not form.validate_on_submit():
        flash("Dữ liệu không hợp lệ", "danger")
        return render_template("assignments/create_edit.html", form=form, mode="create")

    c = Course.query.get_or_404(form.course_id.data)
    if c.teacher_id != current_user.id:
        abort(403)

    a = Assignment(
        course_id=form.course_id.data,
        title=form.title.data.strip(),
        description=form.description.data,
        deadline_at=form.deadline_at.data,
        rubric_json=None,  # rubric đã bỏ khỏi UI MVP
    )
    db.session.add(a)
    db.session.commit()
    log_action(current_user.id, "assignment.create", "Assignment", a.id, {"course_id": a.course_id})
    flash("Tạo bài tập thành công", "success")
    return redirect(url_for("assignments.detail_assignment", assignment_id=a.id))


@bp.get("/<int:assignment_id>")
@login_required
def detail_assignment(assignment_id: int):
    a = Assignment.query.get_or_404(assignment_id)
    require_course_access(a.course_id)

    course = Course.query.get(a.course_id)

    my_groups = []
    if current_user.role == "STUDENT":
        my_groups = (
            db.session.query(Group)
            .join(GroupMember, GroupMember.group_id == Group.id)
            .filter(Group.course_id == a.course_id, GroupMember.user_id == current_user.id)
            .all()
        )

    return render_template("assignments/detail.html", assignment=a, course=course, my_groups=my_groups)
