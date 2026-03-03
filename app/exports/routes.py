from flask import render_template, request, send_file, abort
from flask_login import login_required, current_user
from . import bp
from ..decorators import role_required
from ..extensions import db
from ..models import Assignment, Course, Submission, Grade
from ..utils.export import rows_to_excel_bytes

@bp.get("")
@login_required
@role_required("TEACHER")
def export_index():
    courses = Course.query.filter_by(teacher_id=current_user.id).all()
    course_ids = [c.id for c in courses]
    assignments = Assignment.query.filter(Assignment.course_id.in_(course_ids) if course_ids else False).all()
    return render_template("exports/index.html", courses=courses, assignments=assignments)

@bp.get("/assignment.xlsx")
@login_required
@role_required("TEACHER")
def export_assignment_xlsx():
    assignment_id = request.args.get("assignment_id", type=int)
    if not assignment_id:
        abort(400)

    a = Assignment.query.get_or_404(assignment_id)
    c = Course.query.get_or_404(a.course_id)
    if c.teacher_id != current_user.id:
        abort(403)

    rows = (
        db.session.query(
            Submission.id.label("submission_id"),
            Submission.group_id,
            Submission.submitted_by,
            Submission.submitted_at,
            Submission.link_url,
            Grade.score,
            Grade.feedback,
        )
        .outerjoin(Grade, Grade.submission_id == Submission.id)
        .filter(Submission.assignment_id == assignment_id)
        .order_by(Submission.group_id.asc(), Submission.submitted_at.desc())
        .all()
    )

    headers = ["submission_id", "group_id", "submitted_by", "submitted_at", "link_url", "score", "feedback"]
    data_rows = []
    for r in rows:
        d = r._asdict()
        data_rows.append([d[h] for h in headers])

    buf = rows_to_excel_bytes(headers, data_rows, sheet_name="submissions")

    return send_file(
        buf,
        as_attachment=True,
        download_name=f"assignment_{assignment_id}_submissions.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
