from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired, Length, Email

class GroupForm(FlaskForm):
    course_id = IntegerField("Course ID", validators=[DataRequired()])
    name = StringField("Tên nhóm", validators=[DataRequired(), Length(max=120)])

class AddMemberForm(FlaskForm):
    email = StringField("Email thành viên", validators=[DataRequired(), Email(check_deliverability=False), Length(max=190)])

class SetLeaderForm(FlaskForm):
    leader_user_id = IntegerField("Leader User ID", validators=[DataRequired()])
