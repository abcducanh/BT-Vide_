from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, Length

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(check_deliverability=False), Length(max=190)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=3)])


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField("Current password", validators=[DataRequired(), Length(min=3)])
    new_password = PasswordField("New password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm new password", validators=[DataRequired(), Length(min=6)])

    def validate(self, extra_validators=None):
        ok = super().validate(extra_validators=extra_validators)
        if not ok:
            return False
        if self.new_password.data != self.confirm_password.data:
            self.confirm_password.errors.append("Mật khẩu xác nhận không khớp")
            return False
        return True
