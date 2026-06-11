import os
from flask import Flask, send_from_directory
from extensions import db, login_manager
from models import User
from dotenv import load_dotenv

load_dotenv()


def create_app():
    app = Flask(__name__)

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    app.config['SECRET_KEY']          = os.getenv('SECRET_KEY', 'perpustakaan-dil-secret-2024')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'connect_args': {
            'ssl': {
                'ca': './ca.pem'
            }
        }
    }
    app.config['UPLOAD_FOLDER']       = os.path.join(BASE_DIR, 'static', 'uploads', 'covers')
    app.config['MAX_CONTENT_LENGTH']  = 5 * 1024 * 1024

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from routes.auth       import auth
    from routes.main       import main
    from routes.books      import books
    from routes.peminjaman import peminjaman

    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(books)
    app.register_blueprint(peminjaman)

    @app.route('/covers/<filename>')
    def cover_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    @app.template_filter('rupiah')
    def rupiah_filter(value):
        return f"Rp {int(value):,}".replace(',', '.')

    @app.template_filter('stars')
    def stars_filter(rating):
        full = round(rating)
        return '★' * full + '☆' * (5 - full)

    with app.app_context():
        db.create_all()
        _seed_data()

    return app


def _seed_data():
    from models import User, Rak, Buku
    from werkzeug.security import generate_password_hash

    if not User.query.filter_by(username='aidllahmd').first():
        admin = User(
            nama='Administrator', email='admin@dil.com',
            username='aidllahmd',
            password=generate_password_hash('311206'),
            role='admin'
        )
        db.session.add(admin)

    if Rak.query.count() == 0:
        rak_data = [
            Rak(nama='Rak A1', lokasi='Lantai 1, Sayap Kiri',  kategori='Fiksi, Fantasi, Roman', kapasitas=60, warna='#845EC2'),
            Rak(nama='Rak A2', lokasi='Lantai 1, Sayap Kanan', kategori='Roman, Drama',           kapasitas=50, warna='#FF6B9D'),
            Rak(nama='Rak B2', lokasi='Lantai 1, Tengah',      kategori='Sastra, Puisi',          kapasitas=45, warna='#06D6A0'),
            Rak(nama='Rak C1', lokasi='Lantai 2, Sayap Kiri',  kategori='Pengembangan Diri',      kapasitas=40, warna='#FF9A3C'),
            Rak(nama='Rak D1', lokasi='Lantai 2, Tengah',      kategori='Sejarah, Non-Fiksi',     kapasitas=55, warna='#4FC3F7'),
        ]
        db.session.add_all(rak_data)
        db.session.flush()

        buku_data = [
            Buku(judul='Bumi Manusia',  penulis='Pramoedya Ananta Toer', tahun=1980, genre='Sastra',           stok=3, deskripsi='Novel pertama dari Tetralogi Buru.',  rak_id=rak_data[2].id),
            Buku(judul='Laskar Pelangi',penulis='Andrea Hirata',         tahun=2005, genre='Fiksi',            stok=5, deskripsi='Kisah inspiratif anak-anak Belitung.',rak_id=rak_data[0].id),
            Buku(judul='Atomic Habits', penulis='James Clear',           tahun=2018, genre='Pengembangan Diri',stok=2, deskripsi='Cara membangun kebiasaan baik.',      rak_id=rak_data[3].id),
            Buku(judul='Dilan 1990',    penulis='Pidi Baiq',             tahun=2014, genre='Roman',            stok=4, deskripsi='Kisah cinta remaja di Bandung.',     rak_id=rak_data[1].id),
            Buku(judul='Sapiens',       penulis='Yuval Noah Harari',     tahun=2011, genre='Sejarah',          stok=1, deskripsi='Sejarah singkat umat manusia.',      rak_id=rak_data[4].id),
            Buku(judul='Harry Potter',  penulis='J.K. Rowling',          tahun=1997, genre='Fantasi',          stok=6, deskripsi='Petualangan seru di Hogwarts.',      rak_id=rak_data[0].id),
        ]
        db.session.add_all(buku_data)

    db.session.commit()

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)