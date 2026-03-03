from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, TextAreaField
from wtforms.validators import DataRequired, Optional, Length

class SubmissionForm(FlaskForm):
    assignment_id = IntegerField("Assignment ID", validators=[DataRequired()])
    group_id = IntegerField("Group ID", validators=[DataRequired()])
    link_url = StringField("Link (GitHub/Drive)", validators=[Optional(), Length(max=500)])
    note = TextAreaField("Ghi chú", validators=[Optional()])
