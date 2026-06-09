from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Buku, Peminjaman, User, Rak, Ulasan
from functools import wraps

main = Blueprint('main', __name__)

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Akses ditolak.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated


@main.route('/')
@login_required
def index():
    total_buku   = Buku.query.count()
    total_stok   = db.session.query(db.func.sum(Buku.stok)).scalar() or 0
    dipinjam     = Peminjaman.query.filter_by(status='Dipinjam').count()
    total_genre  = db.session.query(Buku.genre).distinct().count()
    terlambat    = [p for p in Peminjaman.query.filter_by(status='Dipinjam').all() if p.hari_terlambat > 0]
    buku_terbaru = Buku.query.order_by(Buku.created_at.desc()).limit(6).all()
    return render_template('main/index.html',
        total_buku=total_buku, total_stok=total_stok,
        dipinjam=dipinjam, total_genre=total_genre,
        terlambat=terlambat, buku_terbaru=buku_terbaru)


@main.route('/profil', methods=['GET', 'POST'])
@login_required
def profil():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'edit_profil':
            current_user.nama  = request.form.get('nama', current_user.nama).strip()
            current_user.email = request.form.get('email', current_user.email).strip()
            current_user.hp    = request.form.get('hp', '').strip()
            if current_user.role != 'admin':
                current_user.username = request.form.get('username', current_user.username).strip()
            db.session.commit()
            flash('Profil berhasil diperbarui! ✅', 'success')

        elif action == 'ganti_password':
            from werkzeug.security import check_password_hash, generate_password_hash
            lama  = request.form.get('password_lama', '')
            baru  = request.form.get('password_baru', '')
            baru2 = request.form.get('password_baru2', '')
            if current_user.role != 'admin' and not check_password_hash(current_user.password, lama):
                flash('Password lama salah!', 'error')
            elif len(baru) < 6:
                flash('Password baru minimal 6 karakter!', 'error')
            elif baru != baru2:
                flash('Konfirmasi password tidak cocok!', 'error')
            else:
                current_user.password = generate_password_hash(baru)
                db.session.commit()
                flash('Password berhasil diubah! 🔑', 'success')

        return redirect(url_for('main.profil'))

    pinjam_aktif  = Peminjaman.query.filter_by(user_id=current_user.id, status='Dipinjam').all()
    total_pinjam  = Peminjaman.query.filter_by(user_id=current_user.id).count()
    total_ulasan  = Ulasan.query.filter_by(user_id=current_user.id).count()
    return render_template('main/profil.html',
        pinjam_aktif=pinjam_aktif,
        total_pinjam=total_pinjam,
        total_ulasan=total_ulasan)


@main.route('/rak')
@login_required
def rak():
    daftar_rak = Rak.query.all()
    return render_template('main/rak.html', rak_list=daftar_rak)


@main.route('/rak/tambah', methods=['POST'])
@login_required
@admin_required
def tambah_rak():
    nama      = request.form.get('nama', '').strip()
    lokasi    = request.form.get('lokasi', '').strip()
    kategori  = request.form.get('kategori', '').strip()
    kapasitas = int(request.form.get('kapasitas', 30))
    colors    = ['#845EC2','#FF6B9D','#06D6A0','#FF9A3C','#4FC3F7','#FF5E5E']
    warna     = colors[Rak.query.count() % len(colors)]
    if not nama:
        flash('Nama rak wajib diisi!', 'error')
    else:
        r = Rak(nama=nama, lokasi=lokasi, kategori=kategori, kapasitas=kapasitas, warna=warna)
        db.session.add(r)
        db.session.commit()
        flash(f'Rak "{nama}" berhasil ditambahkan! 🗂️', 'success')
    return redirect(url_for('main.rak'))


@main.route('/users')
@login_required
@admin_required
def users():
    daftar_user = User.query.order_by(User.created_at.desc()).all()
    return render_template('main/users.html', users=daftar_user)
