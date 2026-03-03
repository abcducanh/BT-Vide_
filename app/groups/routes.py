from flask import render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from . import bp
from .forms import GroupForm, AddMemberForm, SetLeaderForm
from ..decorators import role_required, require_course_access
from ..extensions import db
from ..models import Course, Group, GroupMember, User, Enrollment
from ..audit import log_action

@bp.get("")
@login_required
def list_groups():
    course_id = request.args.get("course_id", type=int)
    if course_id:
        require_course_access(course_id)
        groups = Group.query.filter_by(course_id=course_id).order_by(Group.created_at.desc()).all()
    else:
        if current_user.role == "TEACHER":
            course_ids = [c.id for c in Course.query.filter_by(teacher_id=current_user.id).all()]
            groups = Group.query.filter(Group.course_id.in_(course_ids)).order_by(Group.created_at.desc()).all()
        else:
            groups = (
                db.session.query(Group)
                .join(GroupMember, GroupMember.group_id == Group.id)
                .filter(GroupMember.user_id == current_user.id)
                .order_by(Group.created_at.desc())
                .all()
            )
    return render_template("groups/list.html", groups=groups)

@bp.post("/create")
@login_required
@role_required("STUDENT")
def create_group():
    """Student tạo nhóm trong course mình đã enrolled.
    - Mỗi học sinh chỉ được thuộc 1 nhóm trong 1 course.
    - Tôn trọng quy định của course: max_groups.
    Auto add creator vào nhóm + set leader = creator.
    """
    form = GroupForm()
    if not form.validate_on_submit():
        flash("Dữ liệu không hợp lệ", "danger")
        return redirect(url_for("courses.list_courses"))

    course_id = form.course_id.data

    # student phải enrolled course
    if Enrollment.query.filter_by(course_id=course_id, user_id=current_user.id).first() is None:
        abort(403)

    course = Course.query.get_or_404(course_id)

    # Nếu đã có nhóm trong course -> không cho tạo mới
    existed_group = (
        db.session.query(Group)
        .join(GroupMember, GroupMember.group_id == Group.id)
        .filter(Group.course_id == course_id, GroupMember.user_id == current_user.id)
        .first()
    )
    if existed_group:
        flash(f"Bạn đã có nhóm trong lớp này: {existed_group.name} (ID {existed_group.id}).", "warning")
        return redirect(url_for("groups.detail_group", group_id=existed_group.id))

    # Check max groups in course (0 = unlimited)
    if course.max_groups and course.max_groups > 0:
        current_count = Group.query.filter_by(course_id=course_id).count()
        if current_count >= course.max_groups:
            flash(f"Lớp đã đạt số nhóm tối đa ({course.max_groups}). Không thể tạo nhóm mới.", "danger")
            return redirect(url_for("courses.detail_course", course_id=course_id))

    g = Group(course_id=course_id, name=form.name.data.strip(), leader_id=current_user.id)
    db.session.add(g)
    db.session.flush()

    db.session.add(GroupMember(group_id=g.id, user_id=current_user.id))
    db.session.commit()

    log_action(current_user.id, "group.create_by_student", "Group", g.id, {"course_id": course_id})
    flash("Tạo nhóm thành công. Bạn đang là trưởng nhóm.", "success")
    return redirect(url_for("groups.detail_group", group_id=g.id))


@bp.get("/<int:group_id>")
@login_required
def detail_group(group_id: int):
    g = Group.query.get_or_404(group_id)
    require_course_access(g.course_id)

    course = Course.query.get_or_404(g.course_id)

    members = (
        db.session.query(User)
        .join(GroupMember, GroupMember.user_id == User.id)
        .filter(GroupMember.group_id == group_id)
        .order_by(User.name.asc())
        .all()
    )

    current_size = len(members)
    max_size = course.max_group_size
    is_full = (max_size is not None and max_size > 0 and current_size >= max_size)

    can_manage = (
        (current_user.role == "TEACHER" and course.teacher_id == current_user.id)
        or (current_user.role == "STUDENT" and g.leader_id == current_user.id)
    )

    add_form = AddMemberForm()
    leader_form = SetLeaderForm()

    return render_template(
        "groups/detail.html",
        group=g,
        course=course,
        members=members,
        add_form=add_form,
        leader_form=leader_form,
        can_manage=can_manage,
        current_size=current_size,
        is_full=is_full,
    )


@bp.post("/<int:group_id>/add-member")
@login_required
def add_member(group_id: int):
    g = Group.query.get_or_404(group_id)
    c = Course.query.get_or_404(g.course_id)

    is_teacher_owner = (current_user.role == "TEACHER" and c.teacher_id == current_user.id)
    is_leader = (current_user.role == "STUDENT" and g.leader_id == current_user.id)
    if not (is_teacher_owner or is_leader):
        abort(403)

    # Check group size limit first
    if c.max_group_size and c.max_group_size > 0:
        current_size = GroupMember.query.filter_by(group_id=group_id).count()
        if current_size >= c.max_group_size:
            flash(f"Nhóm đã đủ số lượng tối đa ({c.max_group_size}).", "warning")
            return redirect(url_for("groups.detail_group", group_id=group_id))

    form = AddMemberForm()
    if not form.validate_on_submit():
        flash("Email không hợp lệ", "danger")
        return redirect(url_for("groups.detail_group", group_id=group_id))

    email = form.email.data.strip().lower()
    u = User.query.filter_by(email=email).first()
    if not u or u.role != "STUDENT":
        flash("Không tìm thấy sinh viên", "warning")
        return redirect(url_for("groups.detail_group", group_id=group_id))

    # Must be enrolled in course (student leader cannot auto-enroll)
    if Enrollment.query.filter_by(course_id=g.course_id, user_id=u.id).first() is None:
        if is_teacher_owner:
            db.session.add(Enrollment(course_id=g.course_id, user_id=u.id))
        else:
            flash("Sinh viên này chưa thuộc lớp. Hãy nhờ giáo viên thêm vào lớp trước.", "warning")
            return redirect(url_for("groups.detail_group", group_id=group_id))

    # Check: student already belongs to another group in this course
    other_group = (
        db.session.query(Group)
        .join(GroupMember, GroupMember.group_id == Group.id)
        .filter(Group.course_id == g.course_id, GroupMember.user_id == u.id)
        .first()
    )
    if other_group and other_group.id != g.id:
        flash(f"Sinh viên này đã có nhóm khác: {other_group.name} (ID {other_group.id}).", "danger")
        db.session.commit()
        return redirect(url_for("groups.detail_group", group_id=group_id))

    existed = GroupMember.query.filter_by(group_id=group_id, user_id=u.id).first()
    if existed:
        flash("Sinh viên đã ở trong nhóm", "info")
        db.session.commit()
        return redirect(url_for("groups.detail_group", group_id=group_id))

    db.session.add(GroupMember(group_id=group_id, user_id=u.id))
    db.session.commit()

    action = "group.add_member" if is_teacher_owner else "group.add_member_by_leader"
    log_action(current_user.id, action, "Group", group_id, {"member_email": email})
    flash("Đã thêm thành viên", "success")
    return redirect(url_for("groups.detail_group", group_id=group_id))


    email = form.email.data.strip().lower()
    u = User.query.filter_by(email=email).first()
    if not u or u.role != "STUDENT":
        flash("Không tìm thấy sinh viên", "warning")
        return redirect(url_for("groups.detail_group", group_id=group_id))

    if Enrollment.query.filter_by(course_id=g.course_id, user_id=u.id).first() is None:
        db.session.add(Enrollment(course_id=g.course_id, user_id=u.id))

    existed = GroupMember.query.filter_by(group_id=group_id, user_id=u.id).first()
    if existed:
        flash("Sinh viên đã ở trong nhóm", "info")
        db.session.commit()
        return redirect(url_for("groups.detail_group", group_id=group_id))

    db.session.add(GroupMember(group_id=group_id, user_id=u.id))
    db.session.commit()
    log_action(current_user.id, "group.add_member", "Group", group_id, {"member_email": email})
    flash("Đã thêm thành viên", "success")
    return redirect(url_for("groups.detail_group", group_id=group_id))

@bp.post("/<int:group_id>/set-leader")
@login_required
@role_required("TEACHER")
def set_leader(group_id: int):
    g = Group.query.get_or_404(group_id)
    c = Course.query.get_or_404(g.course_id)
    if c.teacher_id != current_user.id:
        abort(403)

    form = SetLeaderForm()
    if not form.validate_on_submit():
        flash("Leader id không hợp lệ", "danger")
        return redirect(url_for("groups.detail_group", group_id=group_id))

    leader_id = form.leader_user_id.data
    if GroupMember.query.filter_by(group_id=group_id, user_id=leader_id).first() is None:
        flash("User này không thuộc nhóm", "warning")
        return redirect(url_for("groups.detail_group", group_id=group_id))

    g.leader_id = leader_id
    db.session.commit()
    log_action(current_user.id, "group.set_leader", "Group", group_id, {"leader_id": leader_id})
    flash("Đã cập nhật trưởng nhóm", "success")
    return redirect(url_for("groups.detail_group", group_id=group_id))
