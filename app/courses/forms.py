from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired, Length, Email, NumberRange, Optional

class CourseForm(FlaskForm):
    code = StringField("Mã môn/lớp", validators=[DataRequired(), Length(max=50)])
    name = StringField("Tên môn/lớp", validators=[DataRequired(), Length(max=200)])

    # 0 = unlimited
    max_group_size = IntegerField("Số người tối đa / nhóm (0 = không giới hạn)", validators=[DataRequired(), NumberRange(min=0, max=200)])
    max_groups = IntegerField("Số nhóm tối đa trong lớp (0 = không giới hạn)", validators=[DataRequired(), NumberRange(min=0, max=5000)])

class CourseSettingsForm(FlaskForm):
    # 0 = unlimited
    max_group_size = IntegerField("Số người tối đa / nhóm (0 = không giới hạn)", validators=[DataRequired(), NumberRange(min=0, max=200)])
    max_groups = IntegerField("Số nhóm tối đa trong lớp (0 = không giới hạn)", validators=[DataRequired(), NumberRange(min=0, max=5000)])

class EnrollByEmailForm(FlaskForm):
    email = StringField("Email sinh viên", validators=[DataRequired(), Email(check_deliverability=False), Length(max=190)])
