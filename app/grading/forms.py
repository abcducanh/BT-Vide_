from flask_wtf import FlaskForm
from wtforms import FloatField, TextAreaField
from wtforms.validators import Optional, NumberRange

class GradeForm(FlaskForm):
    score = FloatField("Điểm", validators=[Optional(), NumberRange(min=0)])
    feedback = TextAreaField("Nhận xét", validators=[Optional()])
