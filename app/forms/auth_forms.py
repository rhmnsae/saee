from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models.user import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Ingat saya')
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    name = StringField('Nama Lengkap', validators=[DataRequired(), Length(min=3, max=120)])
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(), 
        Length(min=6, message='Password harus memiliki minimal 6 karakter')
    ])
    confirm_password = PasswordField('Konfirmasi Password', validators=[
        DataRequired(), 
        EqualTo('password', message='Password harus sama')
    ])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username sudah digunakan. Silakan pilih username lain.')
            
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email sudah terdaftar. Silakan gunakan email lain.')

class ProfileForm(FlaskForm):
    username = StringField('Username', render_kw={'readonly': True})
    email = StringField('Email', render_kw={'readonly': True})
    name = StringField('Nama Lengkap', validators=[DataRequired(), Length(min=3, max=120)])
    current_password = PasswordField('Password Saat Ini')
    new_password = PasswordField('Password Baru', validators=[
        Length(min=6, message='Password harus memiliki minimal 6 karakter')
    ])
    confirm_password = PasswordField('Konfirmasi Password Baru', validators=[
        EqualTo('new_password', message='Password harus sama')
    ])
    submit = SubmitField('Simpan Perubahan')