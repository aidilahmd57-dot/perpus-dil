from extensions import db
from flask_login import UserMixin
from datetime import datetime, date


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id         = db.Column(db.Integer, primary_key=True)
    nama       = db.Column(db.String(100), nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    username   = db.Column(db.String(50), unique=True, nullable=False)
    password   = db.Column(db.String(200), nullable=False)
    hp         = db.Column(db.String(20), default='')
    role       = db.Column(db.String(20), default='pengunjung')  # admin / pengunjung
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    peminjaman = db.relationship('Peminjaman', backref='user', lazy=True)
    ulasan     = db.relationship('Ulasan', backref='user', lazy=True)


class Rak(db.Model):
    __tablename__ = 'rak'
    id        = db.Column(db.Integer, primary_key=True)
    nama      = db.Column(db.String(50), nullable=False)
    lokasi    = db.Column(db.String(100), default='')
    kategori  = db.Column(db.String(100), default='')
    kapasitas = db.Column(db.Integer, default=30)
    warna     = db.Column(db.String(20), default='#845EC2')

    buku = db.relationship('Buku', backref='rak_obj', lazy=True)


class Buku(db.Model):
    __tablename__ = 'buku'
    id        = db.Column(db.Integer, primary_key=True)
    judul     = db.Column(db.String(200), nullable=False)
    penulis   = db.Column(db.String(100), nullable=False)
    tahun     = db.Column(db.Integer, default=2024)
    genre     = db.Column(db.String(50), default='Lainnya')
    stok      = db.Column(db.Integer, default=1)
    deskripsi = db.Column(db.Text, default='')
    cover     = db.Column(db.String(300), default='')   # filename di uploads/covers/
    cerita    = db.Column(db.Text, default='')
    rak_id    = db.Column(db.Integer, db.ForeignKey('rak.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    peminjaman = db.relationship('Peminjaman', backref='buku', lazy=True)
    ulasan     = db.relationship('Ulasan', backref='buku', lazy=True)

    @property
    def rata_rating(self):
        if not self.ulasan:
            return 0
        return round(sum(u.rating for u in self.ulasan) / len(self.ulasan), 1)

    @property
    def rak_nama(self):
        return self.rak_obj.nama if self.rak_obj else ''


class Peminjaman(db.Model):
    __tablename__ = 'peminjaman'
    id            = db.Column(db.Integer, primary_key=True)
    buku_id       = db.Column(db.Integer, db.ForeignKey('buku.id'), nullable=False)
    user_id       = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    nama_peminjam = db.Column(db.String(100), nullable=False)
    tanggal       = db.Column(db.Date, default=date.today)
    batas_kembali = db.Column(db.Date, nullable=True)
    status        = db.Column(db.String(20), default='Dipinjam')  # Dipinjam / Dikembalikan
    denda_lunas   = db.Column(db.Boolean, default=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    BATAS_HARI    = 7
    DENDA_PER_HARI = 2000

    @property
    def hari_terlambat(self):
        if self.status == 'Dikembalikan':
            return 0
        diff = (date.today() - self.tanggal).days
        return max(0, diff - self.BATAS_HARI)

    @property
    def total_denda(self):
        return self.hari_terlambat * self.DENDA_PER_HARI


class Ulasan(db.Model):
    __tablename__ = 'ulasan'
    id         = db.Column(db.Integer, primary_key=True)
    buku_id    = db.Column(db.Integer, db.ForeignKey('buku.id'), nullable=False)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    nama       = db.Column(db.String(100), nullable=False)
    rating     = db.Column(db.Integer, default=5)
    teks       = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
