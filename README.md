Aplikasi Web Absensi Karyawan

Aplikasi web full-stack yang dibangun dengan Flask dan MySQL untuk manajemen absensi karyawan. Aplikasi ini memiliki dua peran utama: Admin untuk mengelola data karyawan dan melihat laporan, serta Karyawan untuk melakukan clock-in dan clock-out.

Fitur Utama
Untuk Karyawan
Login aman menggunakan ID Karyawan dan Password.

Dashboard personal yang menampilkan status absensi hari ini.

Tombol untuk melakukan Clock In dan Clock Out secara real-time tanpa refresh halaman.

Tampilan jam dan tanggal digital yang dinamis.

Riwayat absensi pribadi selama 30 hari terakhir.

Untuk Admin
Dashboard terpusat untuk manajemen.

Manajemen Karyawan: Menambah, mengedit, dan menghapus data karyawan melalui antarmuka modal yang intuitif.

Laporan Absensi: Melihat rekapitulasi data absensi dari seluruh karyawan, diurutkan berdasarkan tanggal terbaru.

Stack Teknologi
Backend: Python 3

Framework: Flask

Database: MySQL

Templating: Jinja2

Styling: Tailwind CSS (via CDN)

Interaktivitas: Vanilla JavaScript (Fetch API)

Autentikasi: Flask-Login

Password Hashing: Werkzeug

Prasyarat
Sebelum memulai, pastikan Anda sudah menginstal:

Python 3.8 atau lebih baru

Server Database MySQL atau MariaDB

Panduan Instalasi & Konfigurasi
Ikuti langkah-langkah ini untuk menjalankan aplikasi di lingkungan lokal.

Jika tidak, cukup unduh semua file ke dalam satu folder.

OPSI 1: Buat Virtual Environment
Sangat disarankan untuk menggunakan lingkungan virtual agar dependensi proyek tidak tercampur.

# Untuk Windows

python -m venv venv
venv\Scripts\activate

# Untuk macOS/Linux

python3 -m venv venv
source venv/bin/activate

OPSI 2:
buka terminal, cd to absensi-karyawan

Instal Dependensi
Instal semua library Python yang dibutuhkan dari file requirements.txt.

pip install -r requirements.txt

Setup Database

Buka tool manajemen database Anda (PhpMyAdmin)

Buat database baru. Direkomendasikan bernama attendance_db.

OPSI 1 : Jalankan skrip database.sql pada database yang baru dibuat untuk membuat tabel users dan attendance, serta menambahkan satu user admin default.

OPSI 2 : Copy semua database.sql ke sql secara manual, detailnya:

1. run xampp(mysql + apache) - buka admin diapache
2. buat database baru, namanya attendance_db
3. kalo udah buat, buka tab SQL diatas, copy paste semua isi database.sql dan GO/RUN/Execute intinya jalankan

Konfigurasi Aplikasi

Buka file app.py.

Cari bagian DB_CONFIG dan sesuaikan nilainya dengan kredensial database MySQL Anda (terutama password dan database).

(Opsional untuk Produksi) Ganti nilai app.config['SECRET_KEY'] dengan string acak yang lebih kuat.

Jalankan Aplikasi
Setelah semua konfigurasi selesai, jalankan server Flask.

python app.py #JALANIN PAKE INI DI CMD, PASTIIN UDAH DI DIREKTORI PROJECT ATAU:
cd to absensi-karyawan

Aplikasi akan berjalan di http://127.0.0.1:5001.

Cara Penggunaan
Buka http://127.0.0.1:5001 di browser Anda.

Anda akan diarahkan ke halaman login.

Login sebagai Admin:

ID Karyawan: ADMIN-001

Password: admin123
(Kredensial ini dibuat oleh skrip database.sql. Anda bisa mengubahnya setelah login).

Login sebagai Karyawan:
Gunakan data karyawan yang telah Anda tambahkan melalui dashboard admin.

note : kalo error, direkomendasiin untuk mengubah sesuai dengan local computers, takut ga sesuai bagian hasing password, pake cek.py, caranya jalanin aja, nanti ada outputnya, copy dan ganti coloumn password pake yang ini
