from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField, SubmitField, SelectField, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp


class StudentRegistrationForm(FlaskForm):
    email = StringField('DUT4Life Email', validators=[
        DataRequired(), Email(), Length(max=120),
        Regexp(r'^[a-zA-Z0-9._%+-]+@dut4life\.ac\.za$', message="Only DUT4Life emails allowed!")
    ])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class StudentLoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
  
class CandidateForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    student_number = StringField('Student Number', validators=[DataRequired()])
    achievements = TextAreaField('Achievements', validators=[DataRequired()])
    certificate = FileField('Upload Certificate')
    image = FileField('Upload Profile Image')
    motivation = TextAreaField('Motivation', validators=[DataRequired()])
    party = SelectField('Political Party', choices=[
        ('MK', 'MK'),
        ('EFF', 'EFF'),
        ('SASCO', 'SASCO'),
        ('SADESMO', 'SADESMO')
    ], validators=[DataRequired()])

    position = SelectField('Position Applying For', choices=[
        ('President', 'President'),
        ('Deputy President', 'Deputy President'),
        ('Secretary-General', 'Secretary-General'),
        ('Treasurer', 'Treasurer'),
        ('Academic Officer', 'Academic Officer'),
        ('Sports & Recreation Officer', 'Sports & Recreation Officer'),
        ('Transformation & Student Affairs Officer', 'Transformation & Student Affairs Officer'),
        ('Projects & Development Officer', 'Projects & Development Officer'),
        ('Gender & Disability Representative', 'Gender & Disability Representative')
    ], validators=[DataRequired()])

    submit = SubmitField('Apply')