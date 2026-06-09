# 📚 Perpustakaan DIL

Aplikasi perpustakaan digital berbasis **Flask + SQLite**.

## Struktur File
```
perpustakaan_dil/
├── app.py                  ← Jalankan ini
├── extensions.py           ← SQLAlchemy & LoginManager
├── models.py               ← Model database (User, Buku, Rak, Peminjaman, Ulasan)
├── requirements.txt        ← Daftar library
├── perpustakaan.db         ← Database SQLite (dibuat otomatis)
├── routes/
│   ├── auth.py             ← Login, Register, Logout
│   ├── main.py             ← Beranda, Profil, Rak, Users
│   ├── books.py            ← CRUD Buku, Cerita, Ulasan
│   └── peminjaman.py       ← Pinjam, Kembalikan, Denda
├── templates/
│   ├── base.html           ← Layout utama (header, nav)
│   ├── auth/               ← login.html, register.html
│   ├── main/               ← index.html, rak.html, profil.html, users.html
│   ├── books/              ← index.html, form.html, baca.html, cerita.html
│   └── peminjaman/         ← index.html, form_pinjam.html
└── static/
    ├── css/style.css       ← Semua styling
    ├── js/main.js          ← JavaScript (preview cover, flash, dll)
    └── uploads/covers/     ← Folder cover buku yang diupload
```

## Cara Menjalankan

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Jalankan aplikasi
```bash
python app.py
```

### 3. Buka di browser
```
http://localhost:5000
```

## Akun Default
| Role  | Username   | Password |
|-------|-----------|----------|
| Admin | aidllahmd | 311206   |

Admin bisa langsung tambah user dari halaman Register.

## Fitur
- ✅ Login / Register / Logout
- ✅ Tambah, Edit, Hapus Buku
- ✅ Upload cover buku (JPG/PNG/WebP, maks 5MB)
- ✅ Rak buku dengan lokasi
- ✅ Peminjaman & pengembalian
- ✅ Hitung denda otomatis (Rp 2.000/hari)
- ✅ Tulis isi cerita buku + upload .TXT
- ✅ Rating & ulasan pembaca
- ✅ Halaman profil user
- ✅ Data tersimpan permanen di SQLite
