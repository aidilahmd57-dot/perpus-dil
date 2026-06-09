from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import date, timedelta
from extensions import db
from models import Peminjaman, Buku, User
from functools import wraps

peminjaman = Blueprint('peminjaman', __name__)

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Akses ditolak.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated


@peminjaman.route('/peminjaman')
@login_required
@admin_required
def index():
    daftar = Peminjaman.query.order_by(Peminjaman.created_at.desc()).all()
    return render_template('peminjaman/index.html', peminjaman=daftar)


@peminjaman.route('/peminjaman/pinjam/<int:buku_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def pinjam(buku_id):
    buku = Buku.query.get_or_404(buku_id)
    if buku.stok <= 0:
        flash('Stok buku habis!', 'error')
        return redirect(url_for('books.index'))

    if request.method == 'POST':
        nama = request.form.get('nama_peminjam', '').strip()
        if not nama:
            flash('Nama peminjam wajib diisi!', 'error')
            return render_template('peminjaman/form_pinjam.html', buku=buku)

        tgl   = date.today()
        batas = tgl + timedelta(days=Peminjaman.BATAS_HARI)
        p = Peminjaman(
            buku_id=buku_id,
            user_id=current_user.id,
            nama_peminjam=nama,
            tanggal=tgl,
            batas_kembali=batas,
            status='Dipinjam'
        )
        buku.stok -= 1
        db.session.add(p)
        db.session.commit()
        flash(f'Buku "{buku.judul}" berhasil dipinjam oleh {nama}! 📚', 'success')
        return redirect(url_for('peminjaman.index'))

    return render_template('peminjaman/form_pinjam.html', buku=buku)


@peminjaman.route('/peminjaman/kembalikan/<int:id>', methods=['POST'])
@login_required
@admin_required
def kembalikan(id):
    p = Peminjaman.query.get_or_404(id)
    if p.status == 'Dipinjam':
        p.status = 'Dikembalikan'
        p.buku.stok += 1
        db.session.commit()
        flash('Buku berhasil dikembalikan! ✅', 'success')
    return redirect(url_for('peminjaman.index'))


@peminjaman.route('/peminjaman/bayar-denda/<int:id>', methods=['POST'])
@login_required
@admin_required
def bayar_denda(id):
    p = Peminjaman.query.get_or_404(id)
    p.denda_lunas = True
    db.session.commit()
    flash(f'Denda sebesar Rp {p.total_denda:,} berhasil dibayar! ✅', 'success')
    return redirect(url_for('peminjaman.index'))
