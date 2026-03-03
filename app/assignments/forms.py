from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, DateTimeLocalField
from wtforms.validators import DataRequired, Length, Optional


class AssignmentForm(FlaskForm):
    course_id = IntegerField("Course ID", validators=[DataRequired()])
    title = StringField("Tiêu đề", validators=[DataRequired(), Length(max=200)])
    description = TextAreaField("Mô tả", validators=[Optional()])
    deadline_at = DateTimeLocalField("Deadline", format="%Y-%m-%dT%H:%M", validators=[DataRequired()])
