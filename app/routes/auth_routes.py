from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime

from app.models import db
from app.models.user import User
from app.forms.auth_forms import LoginForm, RegisterForm, ProfileForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Username atau password salah', 'danger')
            return redirect(url_for('auth.login'))
            
        # Login user dan update last_login
        login_user(user, remember=form.remember_me.data)
        user.update_last_login()
        
        flash(f'Selamat datang kembali, {user.username}!', 'success')
        
        # Redirect ke halaman yang diminta sebelumnya (jika ada)
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('main.index')
            
        return redirect(next_page)
        
    return render_template('auth/login.html', title='Login', form=form, hide_nav=True)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    form = RegisterForm()
    if form.validate_on_submit():
        # Cek jika username atau email sudah digunakan
        if User.query.filter_by(username=form.username.data).first():
            flash('Username sudah digunakan. Silakan pilih username lain.', 'danger')
            return redirect(url_for('auth.register'))
            
        if User.query.filter_by(email=form.email.data).first():
            flash('Email sudah terdaftar. Silakan gunakan email lain.', 'danger')
            return redirect(url_for('auth.register'))
        
        # Buat user baru
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            name=form.name.data
        )
        
        # Simpan ke database
        db.session.add(user)
        db.session.commit()
        
        flash('Registrasi berhasil! Silakan login dengan akun Anda.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html', title='Register', form=form, hide_nav=True)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Anda telah berhasil logout', 'info')
    # Clear session
    session.clear()
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    
    if request.method == 'GET':
        # Populate form with current data
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.name.data = current_user.name
    
    if form.validate_on_submit():
        # Update profile information
        current_user.name = form.name.data
        
        # Check if password needs to be updated
        if form.new_password.data:
            if not current_user.check_password(form.current_password.data):
                flash('Password saat ini salah', 'danger')
                return redirect(url_for('auth.profile'))
                
            current_user.set_password(form.new_password.data)
            flash('Password berhasil diperbarui', 'success')
            
        db.session.commit()
        flash('Profil berhasil diperbarui', 'success')
        return redirect(url_for('auth.profile'))
        
    return render_template('auth/profile.html', title='Profil', form=form)