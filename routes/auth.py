from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models import User

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)
            flash(f'Selamat datang, {user.nama}! 👋', 'success')
            return redirect(url_for('main.index'))
        flash('Username/email atau password salah!', 'error')
    return render_template('auth/login.html')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        nama     = request.form.get('nama', '').strip()
        email    = request.form.get('email', '').strip()
        hp       = request.form.get('hp', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')

        if not all([nama, email, username, password]):
            flash('Semua field wajib diisi!', 'error')
        elif password != confirm:
            flash('Konfirmasi password tidak cocok!', 'error')
        elif len(password) < 6:
            flash('Password minimal 6 karakter!', 'error')
        elif User.query.filter_by(username=username).first():
            flash('Username sudah dipakai!', 'error')
        elif User.query.filter_by(email=email).first():
            flash('Email sudah terdaftar!', 'error')
        else:
            user = User(
                nama=nama, email=email, hp=hp, username=username,
                password=generate_password_hash(password), role='pengunjung'
            )
            db.session.add(user)
            db.session.commit()
            flash('Registrasi berhasil! Silakan login.', 'success')
            return redirect(url_for('auth.login'))
    return render_template('auth/register.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Berhasil logout.', 'info')
    return redirect(url_for('auth.login'))
