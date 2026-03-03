from flask import render_template, redirect, url_for, flash, current_app, abort, request
from flask_login import login_required, current_user
from datetime import datetime
from . import bp
from .forms import SubmissionForm
from ..extensions import db
from ..models import Assignment, Submission, SubmissionFile, Group, Course, Grade
from ..decorators import require_course_access, require_student_in_group, role_required
from ..utils.storage import allowed_file, save_upload
from ..utils.time import is_late
from ..audit import log_action

@bp.post("/create")
@login_required
def create_submission():
    form = SubmissionForm()
    if not form.validate_on_submit():
        flash("Dữ liệu không hợp lệ", "danger")
        return redirect(url_for("dashboard"))

    assignment_id = form.assignment_id.data
    group_id = form.group_id.data

    a = Assignment.query.get_or_404(assignment_id)
    g = Group.query.get_or_404(group_id)
    if g.course_id != a.course_id:
        flash("Nhóm không thuộc bài tập này", "danger")
        return redirect(url_for("assignments.detail_assignment", assignment_id=assignment_id))

    require_course_access(a.course_id)
    require_student_in_group(group_id)

    sub = Submission(
        assignment_id=assignment_id,
        group_id=group_id,
        submitted_by=current_user.id,
        submitted_at=datetime.utcnow(),
        link_url=form.link_url.data.strip() if form.link_url.data else None,
        note=form.note.data,
    )
    db.session.add(sub)
    db.session.flush()

    f = request.files.get("file")
    if f and f.filename:
        if not allowed_file(f.filename):
            db.session.rollback()
            flash("File không được hỗ trợ", "danger")
            return redirect(url_for("assignments.detail_assignment", assignment_id=assignment_id))

        rel_dir = f"{a.course_id}/{assignment_id}/{group_id}/{sub.id}"
        rel_path, saved_name, size = save_upload(f, current_app.config["UPLOAD_DIR"], rel_dir)

        db.session.add(SubmissionFile(
            submission_id=sub.id,
            file_path=rel_path,
            original_name=saved_name,
            size=size
        ))

    db.session.commit()
    log_action(current_user.id, "submission.create", "Submission", sub.id, {"assignment_id": assignment_id, "group_id": group_id})

    flash("Nộp bài thành công (đã tạo phiên bản mới).", "success")
    return redirect(url_for("submissions.group_history", group_id=group_id, assignment_id=assignment_id))

@bp.get("/group/<int:group_id>/history")
@login_required
def group_history(group_id: int):
    assignment_id = request.args.get("assignment_id", type=int)
    if not assignment_id:
        abort(400)

    g = Group.query.get_or_404(group_id)
    a = Assignment.query.get_or_404(assignment_id)
    if g.course_id != a.course_id:
        abort(400)

    require_course_access(a.course_id)
    require_student_in_group(group_id)

    submissions = (
        Submission.query
        .filter_by(group_id=group_id, assignment_id=assignment_id)
        .order_by(Submission.submitted_at.desc())
        .all()
    )

    sub_ids = [s.id for s in submissions]
    grade_map = {gr.submission_id: gr for gr in Grade.query.filter(Grade.submission_id.in_(sub_ids) if sub_ids else False).all()}

    files = SubmissionFile.query.filter(SubmissionFile.submission_id.in_(sub_ids) if sub_ids else False).all()
    file_map = {}
    for sf in files:
        file_map.setdefault(sf.submission_id, []).append(sf)

    return render_template(
        "submissions/group_history.html",
        group=g,
        assignment=a,
        submissions=submissions,
        grade_map=grade_map,
        file_map=file_map,
        is_late=is_late
    )

@bp.get("/assignment/<int:assignment_id>/all")
@login_required
@role_required("TEACHER")
def assignment_all(assignment_id: int):
    a = Assignment.query.get_or_404(assignment_id)
    c = Course.query.get_or_404(a.course_id)
    if c.teacher_id != current_user.id:
        abort(403)

    all_subs = (
        Submission.query
        .filter_by(assignment_id=assignment_id)
        .order_by(Submission.group_id.asc(), Submission.submitted_at.desc())
        .all()
    )

    latest = {}
    for s in all_subs:
        if s.group_id not in latest:
            latest[s.group_id] = s

    sub_ids = [s.id for s in latest.values()]
    grade_map = {g.submission_id: g for g in Grade.query.filter(Grade.submission_id.in_(sub_ids) if sub_ids else False).all()}

    groups = Group.query.filter_by(course_id=a.course_id).all()

    return render_template(
        "submissions/assignment_all.html",
        assignment=a,
        course=c,
        groups=groups,
        latest=latest,
        grade_map=grade_map,
        is_late=is_late
    )
