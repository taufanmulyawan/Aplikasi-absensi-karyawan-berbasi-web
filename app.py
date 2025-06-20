import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from mysql.connector import Error
from datetime import datetime

# ==============================================================================
# KONFIGURASI APLIKASI
# ==============================================================================
app = Flask(__name__)
# Ganti dengan secret key yang kuat dan acak untuk produksi
app.config['SECRET_KEY'] = 'kunci-rahasia-yang-sangat-aman-dan-sulit-ditebak'

# Konfigurasi Database MySQL
# GANTI DENGAN KREDENSIAL DATABASE ANDA
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root', 
    'password': '', # Isi password database Anda, jika ada
    'database': 'attendance_db' # Pastikan nama database sesuai
}

# Inisialisasi Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # Rute yang dituju jika user belum login
login_manager.login_message = "Silakan login untuk mengakses halaman ini."
login_manager.login_message_category = "info"

# ==============================================================================
# KONEKSI DATABASE
# ==============================================================================
def get_db_connection():
    """Membuat dan mengembalikan koneksi dan cursor ke database."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        # Menggunakan dictionary=True agar hasil query bisa diakses seperti dictionary
        return conn, conn.cursor(dictionary=True)
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        # Jika koneksi gagal, aplikasi tidak bisa berjalan.
        # Di aplikasi nyata, ini harus ditangani dengan lebih baik.
        return None, None

# ==============================================================================
# MODEL PENGGUNA (USER) UNTUK FLASK-LOGIN
# ==============================================================================
class User(UserMixin):
    """Model untuk pengguna dengan integrasi Flask-Login."""
    def __init__(self, id, name, email, employee_id, role, password_hash):
        self.id = id
        self.name = name
        self.email = email
        self.employee_id = employee_id
        self.role = role
        self.password_hash = password_hash

    def check_password(self, password):
        """Memeriksa apakah password yang diberikan cocok dengan hash."""
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    """Callback Flask-Login untuk memuat pengguna dari database berdasarkan ID."""
    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user_data = cursor.fetchone()
            if user_data:
                return User(
                    id=user_data['id'],
                    name=user_data['name'],
                    email=user_data['email'],
                    employee_id=user_data['employee_id'],
                    role=user_data['role'],
                    password_hash=user_data['password']
                )
        except Error as e:
            print(f"Error loading user: {e}")
        finally:
            cursor.close()
            conn.close()
    return None

# ==============================================================================
# RUTE AUTENTIKASI (LOGIN & LOGOUT)
# ==============================================================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Menangani proses login pengguna."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form_data = {}
    if request.method == 'POST':
        # Ambil data dari form dan bersihkan spasi pada employee_id
        employee_id = request.form.get('employee_id', '').strip()
        password = request.form.get('password', '')
        form_data = request.form # Simpan data form untuk dikirim kembali jika gagal

        if not employee_id or not password:
            flash('ID Karyawan dan Password harus diisi.', 'danger')
            # Kirim kembali data form agar ID tidak hilang
            return render_template('login.html', form_data=form_data)

        conn, cursor = get_db_connection()
        if not (conn and cursor):
            flash("Gagal terhubung ke server database.", "danger")
            return render_template('login.html', form_data=form_data)

        try:
            cursor.execute("SELECT * FROM users WHERE employee_id = %s", (employee_id,))
            user_data = cursor.fetchone()

            if user_data:
                user_instance = User(
                    id=user_data['id'], name=user_data['name'], email=user_data['email'],
                    employee_id=user_data['employee_id'], role=user_data['role'], password_hash=user_data['password']
                )

                # --- BAGIAN PENTING UNTUK DEBUGGING ---
                # Tambahkan print() ini untuk sementara waktu di terminal Anda
                print("\n--- DEBUGGING LOGIN ---")
                print(f"Input ID       : '{employee_id}'")
                print(f"Input Password : '{password}'")
                print(f"Stored Hash    : '{user_instance.password_hash}'")
                is_match = user_instance.check_password(password)
                print(f"Password Match?: {is_match}")
                print("-----------------------\n")
                # ----------------------------------------

                if is_match:
                    login_user(user_instance)
                    flash('Login berhasil! Selamat datang kembali.', 'success')
                    return redirect(url_for('index'))

            flash('ID Karyawan atau Password salah.', 'danger')

        except Error as e:
            print(f"Database error during login: {e}")
            flash("Terjadi kesalahan pada server saat mencoba login.", "danger")
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    # Kirim form_data ke template
    return render_template('login.html', form_data=form_data)

@app.route('/logout')
@login_required
def logout():
    """Menangani proses logout pengguna."""
    logout_user()
    flash('Anda telah berhasil logout.', 'success')
    return redirect(url_for('login'))

# ==============================================================================
# RUTE UTAMA & DASHBOARD
# ==============================================================================
@app.route('/')
@login_required
def index():
    """Mengarahkan pengguna ke dashboard yang sesuai berdasarkan peran."""
    if current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    else:
        return redirect(url_for('employee_dashboard'))

@app.route('/dashboard')
@login_required
def employee_dashboard():
    """Menampilkan dashboard untuk karyawan."""
    if current_user.role != 'employee':
        flash("Akses ditolak. Halaman ini hanya untuk karyawan.", "warning")
        return redirect(url_for('index'))

    conn, cursor = get_db_connection()
    if not (conn and cursor):
        flash("Gagal memuat data dashboard.", "danger")
        return render_template('employee_dashboard.html', attendance_history=[], attendance_status='error')

    today = datetime.now().date()
    
    # Cek status absensi hari ini
    cursor.execute(
        "SELECT * FROM attendance WHERE user_id = %s AND date = %s",
        (current_user.id, today)
    )
    today_attendance = cursor.fetchone()
    
    status = "not_clocked_in"
    if today_attendance:
        status = "clocked_in" if not today_attendance['clock_out_time'] else "completed"
            
    # Ambil riwayat absensi 30 hari terakhir
    cursor.execute(
        "SELECT * FROM attendance WHERE user_id = %s ORDER BY date DESC, clock_in_time DESC LIMIT 30",
        (current_user.id,)
    )
    history = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template(
        'employee_dashboard.html', 
        attendance_history=history, 
        attendance_status=status
    )

# ==============================================================================
# RUTE ADMIN (MANAJEMEN KARYAWAN & LAPORAN)
# ==============================================================================
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    """Menampilkan dashboard untuk admin."""
    if current_user.role != 'admin':
        flash("Anda tidak memiliki hak akses ke halaman ini.", "danger")
        return redirect(url_for('index'))

    conn, cursor = get_db_connection()
    if not (conn and cursor):
        flash("Gagal memuat data dashboard.", "danger")
        return render_template('admin_dashboard.html', employees=[], attendance_records=[])

    # Ambil semua karyawan
    cursor.execute("SELECT id, name, email, employee_id, role FROM users ORDER BY name")
    employees = cursor.fetchall()

    # Ambil semua data absensi
    cursor.execute(
        """
        SELECT a.id, u.name, u.employee_id, a.date, a.clock_in_time, a.clock_out_time
        FROM attendance a JOIN users u ON a.user_id = u.id
        ORDER BY a.date DESC, a.clock_in_time DESC
        """
    )
    attendance_records = cursor.fetchall()
    
    cursor.close()
    conn.close()

    return render_template('admin_dashboard.html', employees=employees, attendance_records=attendance_records)

@app.route('/admin/employees/add', methods=['POST'])
@login_required
def add_employee():
    """Menambah karyawan baru."""
    if current_user.role != 'admin':
        return jsonify({'status': 'error', 'message': 'Akses ditolak'}), 403
    
    name = request.form.get('name')
    email = request.form.get('email')
    employee_id = request.form.get('employee_id')
    password = request.form.get('password')
    role = request.form.get('role', 'employee')

    if not all([name, email, employee_id, password]):
        flash('Semua field wajib diisi.', 'danger')
        return redirect(url_for('admin_dashboard'))

    hashed_password = generate_password_hash(password)
    conn, cursor = get_db_connection()
    if not (conn and cursor):
        flash("Gagal terhubung ke database.", "danger")
        return redirect(url_for('admin_dashboard'))

    try:
        cursor.execute(
            "INSERT INTO users (name, email, password, employee_id, role) VALUES (%s, %s, %s, %s, %s)",
            (name, email, hashed_password, employee_id, role)
        )
        conn.commit()
        flash('Karyawan baru berhasil ditambahkan.', 'success')
    except mysql.connector.IntegrityError:
        flash('Email atau ID Karyawan sudah ada. Gunakan yang lain.', 'danger')
    finally:
        cursor.close()
        conn.close()
        
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/employees/edit/<int:user_id>', methods=['POST'])
@login_required
def edit_employee(user_id):
    """Mengedit data karyawan."""
    if current_user.role != 'admin':
        return jsonify({'status': 'error', 'message': 'Akses ditolak'}), 403
         
    name = request.form.get('edit_name')
    email = request.form.get('edit_email')
    employee_id = request.form.get('edit_employee_id')
    role = request.form.get('edit_role')

    conn, cursor = get_db_connection()
    if not (conn and cursor):
        flash("Gagal terhubung ke database.", "danger")
        return redirect(url_for('admin_dashboard'))
    
    try:
        cursor.execute(
            "UPDATE users SET name=%s, email=%s, employee_id=%s, role=%s WHERE id=%s",
            (name, email, employee_id, role, user_id)
        )
        conn.commit()
        flash('Data karyawan berhasil diperbarui.', 'success')
    except mysql.connector.IntegrityError:
        flash('Email atau ID Karyawan sudah digunakan oleh pengguna lain.', 'danger')
    finally:
        cursor.close()
        conn.close()
        
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/employees/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_employee(user_id):
    """Menghapus karyawan."""
    if current_user.role != 'admin':
        return jsonify({'status': 'error', 'message': 'Akses ditolak'}), 403

    conn, cursor = get_db_connection()
    if not (conn and cursor):
        flash("Gagal terhubung ke database.", "danger")
        return redirect(url_for('admin_dashboard'))

    try:
        cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
        conn.commit()
        flash('Karyawan berhasil dihapus.', 'success')
    except Error as e:
        flash(f'Gagal menghapus karyawan: {e}', 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('admin_dashboard'))

# ==============================================================================
# RUTE API UNTUK ABSENSI (dipaanggil via JavaScript)
# ==============================================================================
@app.route('/api/attendance/clock_in', methods=['POST'])
@login_required
def api_clock_in():
    """API endpoint untuk clock-in."""
    conn, cursor = get_db_connection()
    if not (conn and cursor):
        return jsonify({'status': 'error', 'message': 'Koneksi database gagal'}), 500

    today = datetime.now().date()
    # Cek apakah sudah ada clock in hari ini
    cursor.execute(
        "SELECT id FROM attendance WHERE user_id = %s AND date = %s",
        (current_user.id, today)
    )
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({'status': 'error', 'message': 'Anda sudah melakukan clock-in hari ini.'}), 409 # 409 Conflict

    clock_in_time = datetime.now()
    try:
        cursor.execute(
            "INSERT INTO attendance (user_id, clock_in_time, date) VALUES (%s, %s, %s)",
            (current_user.id, clock_in_time, today)
        )
        conn.commit()
        return jsonify({
            'status': 'success', 
            'message': 'Clock-in berhasil!',
            'time': clock_in_time.strftime('%H:%M:%S')
        })
    except Error as e:
        return jsonify({'status': 'error', 'message': f'Terjadi kesalahan server: {e}'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/attendance/clock_out', methods=['POST'])
@login_required
def api_clock_out():
    """API endpoint untuk clock-out."""
    conn, cursor = get_db_connection()
    if not (conn and cursor):
        return jsonify({'status': 'error', 'message': 'Koneksi database gagal'}), 500

    today = datetime.now().date()
    clock_out_time = datetime.now()
    
    try:
        # Update hanya jika ada clock_in dan belum ada clock_out
        cursor.execute(
            """
            UPDATE attendance SET clock_out_time = %s 
            WHERE user_id = %s AND date = %s AND clock_out_time IS NULL
            """,
            (clock_out_time, current_user.id, today)
        )
        # cursor.rowcount akan bernilai 0 jika tidak ada baris yang cocok/diupdate
        if cursor.rowcount == 0:
             return jsonify({'status': 'error', 'message': 'Tidak ada sesi clock-in yang aktif untuk di-clock-out.'}), 404 # 404 Not Found

        conn.commit()
        return jsonify({
            'status': 'success', 
            'message': 'Clock-out berhasil!',
            'time': clock_out_time.strftime('%H:%M:%S')
        })
    except Error as e:
        return jsonify({'status': 'error', 'message': f'Terjadi kesalahan server: {e}'}), 500
    finally:
        cursor.close()
        conn.close()

# ==============================================================================
# JALANKAN APLIKASI
# ==============================================================================
if __name__ == '__main__':
    # debug=True untuk mode pengembangan, matikan di mode produksi
    # port=5001 agar tidak bentrok jika ada service lain di port 5000
    app.run(host='0.0.0.0', port=5001, debug=True)
