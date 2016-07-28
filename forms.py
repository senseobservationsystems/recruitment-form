from flask.ext.wtf import Form
from wtforms.fields import StringField, DateTimeField, RadioField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, URL
from widgets import DatePickerWidget
from app import POSITION


class ApplicantForm(Form):
    name = StringField('Name', [DataRequired()])
    email = StringField('Email', [Email()])
    test_date = DateTimeField('Test Date', format="%m/%d/%Y %H:%M", widget=DatePickerWidget(), )
    position = SelectField('Position', choices=[(pos, pos) for pos in POSITION.keys()])
    cover_letter = TextAreaField('Cover Letter')
    linkedin = StringField('LinkedIn Profile', [URL()])
    github = StringField('Github Account', [URL()])
    english_proficiency = RadioField('English Proficiency', choices=[(str(x), str(x)) for x in range(1, 6)])
