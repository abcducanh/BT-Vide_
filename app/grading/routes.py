from flask import render_template, redirect, url_for, flash, abort, current_app, request
from flask_login import login_required, current_user
from datetime import datetime
from . import bp
from .forms import GradeForm
from ..decorators import role_required
from ..extensions import db
from ..models import Submission, Grade, Assignment, Course, SubmissionFile
from ..utils.storage import allowed_file, save_upload
from ..audit import log_action

@bp.get("/<int:submission_id>")
@login_required
@role_required("TEACHER")
def grade_page(submission_id: int):
    sub = Submission.query.get_or_404(submission_id)
    a = Assignment.query.get_or_404(sub.assignment_id)
    c = Course.query.get_or_404(a.course_id)
    if c.teacher_id != current_user.id:
        abort(403)

    grade = Grade.query.filter_by(submission_id=submission_id).first()
    form = GradeForm()
    if grade:
        form.score.data = grade.score
        form.feedback.data = grade.feedback

    files = SubmissionFile.query.filter_by(submission_id=submission_id).all()
    return render_template("grading/grade.html", submission=sub, assignment=a, course=c, form=form, grade=grade, files=files)

@bp.post("/<int:submission_id>")
@login_required
@role_required("TEACHER")
def grade_post(submission_id: int):
    sub = Submission.query.get_or_404(submission_id)
    a = Assignment.query.get_or_404(sub.assignment_id)
    c = Course.query.get_or_404(a.course_id)
    if c.teacher_id != current_user.id:
        abort(403)

    form = GradeForm()
    if not form.validate_on_submit():
        flash("Dữ liệu không hợp lệ", "danger")
        return redirect(url_for("grading.grade_page", submission_id=submission_id))

    grade = Grade.query.filter_by(submission_id=submission_id).first()
    if grade is None:
        grade = Grade(submission_id=submission_id, graded_by=current_user.id)
        db.session.add(grade)

    grade.score = form.score.data
    grade.feedback = form.feedback.data
    grade.graded_by = current_user.id
    grade.graded_at = datetime.utcnow()

    f = request.files.get("return_file")
    if f and f.filename:
        if not allowed_file(f.filename):
            flash("File trả lời không được hỗ trợ", "warning")
        else:
            rel_dir = f"returns/{a.course_id}/{a.id}/{sub.group_id}/{sub.id}"
            rel_path, saved_name, size = save_upload(f, current_app.config["UPLOAD_DIR"], rel_dir)
            grade.return_file_path = rel_path

    db.session.commit()
    log_action(current_user.id, "grade.upsert", "Submission", submission_id, {"score": grade.score})
    flash("Đã lưu chấm điểm", "success")
    return redirect(url_for("grading.grade_page", submission_id=submission_id))
