from pathlib import Path
from flask import abort, current_app, send_file
from flask_login import login_required, current_user
from . import bp
from ..models import SubmissionFile, Submission, Assignment, Course, Grade
from ..decorators import require_course_access, require_student_in_group

def _resolve_under_uploads(rel_path: str) -> Path:
    base = Path(current_app.config["UPLOAD_DIR"]).resolve()
    target = (base / rel_path).resolve()
    # prevent path traversal
    if base not in target.parents and base != target:
        abort(403)
    if not target.exists():
        abort(404)
    return target

@bp.get("/submission-file/<int:file_id>")
@login_required
def download_submission_file(file_id: int):
    sf = SubmissionFile.query.get_or_404(file_id)
    sub = Submission.query.get_or_404(sf.submission_id)
    a = Assignment.query.get_or_404(sub.assignment_id)

    # Teacher: owns course; Student: enrolled + in group
    require_course_access(a.course_id)
    require_student_in_group(sub.group_id)

    path = _resolve_under_uploads(sf.file_path)
    return send_file(path, as_attachment=True, download_name=sf.original_name)

@bp.get("/return-file/<int:submission_id>")
@login_required
def download_return_file(submission_id: int):
    sub = Submission.query.get_or_404(submission_id)
    a = Assignment.query.get_or_404(sub.assignment_id)
    require_course_access(a.course_id)
    require_student_in_group(sub.group_id)

    gr = Grade.query.filter_by(submission_id=submission_id).first()
    if not gr or not gr.return_file_path:
        abort(404)

    path = _resolve_under_uploads(gr.return_file_path)
    # filename: use last path part
    return send_file(path, as_attachment=True, download_name=Path(gr.return_file_path).name)
