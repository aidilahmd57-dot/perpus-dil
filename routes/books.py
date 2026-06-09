import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from extensions import db
from models import Buku, Rak, Ulasan
from functools import wraps

books = Blueprint('books', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Akses ditolak. Hanya admin yang bisa melakukan ini.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_cover(file):
    if file and file.filename and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Buat nama unik agar tidak tertimpa
        import uuid
        ext = filename.rsplit('.', 1)[1].lower()
        unique_name = f"{uuid.uuid4().hex}.{ext}"
        path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name)
        file.save(path)
        return unique_name
    return ''


@books.route('/buku')
@login_required
def index():
    search = request.args.get('q', '')
    genre  = request.args.get('genre', '')
    query  = Buku.query
    if search:
        query = query.filter(
            (Buku.judul.ilike(f'%{search}%')) | (Buku.penulis.ilike(f'%{search}%'))
        )
    if genre:
        query = query.filter_by(genre=genre)
    daftar_buku = query.order_by(Buku.created_at.desc()).all()
    genres = db.session.query(Buku.genre).distinct().all()
    genres = [g[0] for g in genres]
    return render_template('books/index.html', buku=daftar_buku, genres=genres,
                           search=search, selected_genre=genre)


@books.route('/buku/tambah', methods=['GET', 'POST'])
@login_required
@admin_required
def tambah():
    rak_list = Rak.query.all()
    if request.method == 'POST':
        judul    = request.form.get('judul', '').strip()
        penulis  = request.form.get('penulis', '').strip()
        tahun    = request.form.get('tahun', 2024)
        genre    = request.form.get('genre', 'Lainnya')
        stok     = request.form.get('stok', 1)
        deskripsi = request.form.get('deskripsi', '').strip()
        rak_id   = request.form.get('rak_id') or None

        if not judul or not penulis:
            flash('Judul dan penulis wajib diisi!', 'error')
            return render_template('books/form.html', rak_list=rak_list, mode='tambah')

        cover_filename = ''
        if 'cover' in request.files:
            cover_filename = save_cover(request.files['cover'])

        buku = Buku(
            judul=judul, penulis=penulis, tahun=int(tahun),
            genre=genre, stok=int(stok), deskripsi=deskripsi,
            cover=cover_filename, rak_id=int(rak_id) if rak_id else None
        )
        db.session.add(buku)
        db.session.commit()
        flash(f'Buku "{judul}" berhasil ditambahkan! 📚', 'success')
        return redirect(url_for('books.index'))

    return render_template('books/form.html', rak_list=rak_list, mode='tambah')


@books.route('/buku/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    buku     = Buku.query.get_or_404(id)
    rak_list = Rak.query.all()

    if request.method == 'POST':
        buku.judul    = request.form.get('judul', buku.judul).strip()
        buku.penulis  = request.form.get('penulis', buku.penulis).strip()
        buku.tahun    = int(request.form.get('tahun', buku.tahun))
        buku.genre    = request.form.get('genre', buku.genre)
        buku.stok     = int(request.form.get('stok', buku.stok))
        buku.deskripsi = request.form.get('deskripsi', buku.deskripsi).strip()
        rak_id        = request.form.get('rak_id') or None
        buku.rak_id   = int(rak_id) if rak_id else None

        if 'cover' in request.files and request.files['cover'].filename:
            # Hapus cover lama
            if buku.cover:
                old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], buku.cover)
                if os.path.exists(old_path):
                    os.remove(old_path)
            buku.cover = save_cover(request.files['cover'])

        db.session.commit()
        flash(f'Buku "{buku.judul}" berhasil diupdate! ✅', 'success')
        return redirect(url_for('books.index'))

    return render_template('books/form.html', buku=buku, rak_list=rak_list, mode='edit')


@books.route('/buku/hapus/<int:id>', methods=['POST'])
@login_required
@admin_required
def hapus(id):
    buku = Buku.query.get_or_404(id)
    if buku.cover:
        path = os.path.join(current_app.config['UPLOAD_FOLDER'], buku.cover)
        if os.path.exists(path):
            os.remove(path)
    db.session.delete(buku)
    db.session.commit()
    flash(f'Buku "{buku.judul}" berhasil dihapus.', 'info')
    return redirect(url_for('books.index'))


@books.route('/buku/cerita/<int:id>', methods=['GET', 'POST'])
@login_required
def cerita(id):
    buku = Buku.query.get_or_404(id)
    if request.method == 'POST':
        if current_user.role != 'admin':
            flash('Hanya admin yang bisa mengedit cerita.', 'error')
            return redirect(url_for('books.cerita', id=id))

        # Bisa dari textarea atau upload file
        if 'file_cerita' in request.files and request.files['file_cerita'].filename:
            f = request.files['file_cerita']
            ext = f.filename.rsplit('.', 1)[-1].lower() if '.' in f.filename else ''
            if ext == 'txt':
                buku.cerita = f.read().decode('utf-8', errors='replace')
            else:
                flash('Hanya file .txt yang didukung untuk upload langsung. Gunakan fitur PDF di halaman baca.', 'warning')
        else:
            buku.cerita = request.form.get('cerita', '')

        db.session.commit()
        flash('Cerita berhasil disimpan! 📖', 'success')
        return redirect(url_for('books.cerita', id=id))

    return render_template('books/cerita.html', buku=buku)


@books.route('/buku/baca/<int:id>')
@login_required
def baca(id):
    buku   = Buku.query.get_or_404(id)
    ulasan = Ulasan.query.filter_by(buku_id=id).order_by(Ulasan.created_at.desc()).all()
    return render_template('books/baca.html', buku=buku, ulasan=ulasan)


@books.route('/buku/ulasan/<int:id>', methods=['POST'])
@login_required
def ulasan(id):
    buku  = Buku.query.get_or_404(id)
    nama  = request.form.get('nama', current_user.nama).strip()
    rating = int(request.form.get('rating', 5))
    teks  = request.form.get('teks', '').strip()
    u = Ulasan(buku_id=id, user_id=current_user.id, nama=nama,
               rating=max(1, min(5, rating)), teks=teks)
    db.session.add(u)
    db.session.commit()
    flash('Ulasan berhasil dikirim! ⭐', 'success')
    return redirect(url_for('books.baca', id=id))
