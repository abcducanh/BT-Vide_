from flask import render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import bp
from .forms import LoginForm, ChangePasswordForm
from ..models import User
from ..extensions import db
from ..audit import log_action


@bp.get("/login")
def login():
    form = LoginForm()
    return render_template("auth/login.html", form=form)


@bp.post("/login")
def login_post():
    form = LoginForm()
    if not form.validate_on_submit():
        flash("Dữ liệu không hợp lệ", "danger")
        return render_template("auth/login.html", form=form)

    email = form.email.data.strip().lower()
    pw = form.password.data
    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(pw):
        flash("Sai email hoặc mật khẩu", "danger")
        return render_template("auth/login.html", form=form)

    login_user(user)
    log_action(user.id, "auth.login", "User", user.id)
    return redirect(url_for("dashboard"))


@bp.get("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@bp.get("/change-password")
@login_required
def change_password():
    form = ChangePasswordForm()
    return render_template("auth/change_password.html", form=form)


@bp.post("/change-password")
@login_required
def change_password_post():
    form = ChangePasswordForm()
    if not form.validate_on_submit():
        flash("Dữ liệu không hợp lệ", "danger")
        return render_template("auth/change_password.html", form=form)

    if not current_user.check_password(form.current_password.data):
        flash("Mật khẩu hiện tại không đúng", "danger")
        return render_template("auth/change_password.html", form=form)

    current_user.set_password(form.new_password.data)
    db.session.commit()
    log_action(current_user.id, "auth.change_password", "User", current_user.id)
    flash("Đổi mật khẩu thành công", "success")
    return redirect(url_for("dashboard"))
