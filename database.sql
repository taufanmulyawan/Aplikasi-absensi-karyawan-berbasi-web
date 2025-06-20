-- Skema untuk Aplikasi Absensi Karyawan
-- Database: direkomendasikan bernama 'attendance_db' #karna udah sesuai sama backend flask

-- Pastikan membuat database sebelum menjalankan skrip ini.
-- CREATE DATABASE attendance_db;
-- USE attendance_db;

-- Tabel untuk menyimpan data pengguna (karyawan dan admin)
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL, -- Password akan disimpan dalam bentuk hash
    employee_id VARCHAR(50) UNIQUE NOT NULL,
    role ENUM('admin', 'employee') NOT NULL DEFAULT 'employee'
);

-- Tabel untuk mencatat absensi
CREATE TABLE attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    clock_in_time DATETIME NOT NULL,
    clock_out_time DATETIME NULL, -- Bisa NULL jika belum clock-out
    `date` DATE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- (Opsional) Tambahkan pengguna admin awal untuk login pertama kali
-- Ganti 'hashed_password_here' dengan hash dari password yang Anda inginkan
-- Anda bisa membuat hash-nya melalui skrip Python terpisah atau saat aplikasi berjalan
-- Contoh password: 'admin123'
INSERT INTO `users` (`name`, `email`, `password`, `employee_id`, `role`) 
VALUES 
(
  'Admin Utama',
  'admin@kantor.com',
  'scrypt:32768:8:1$586knmB5gWn6KTE4$2fe116558ca8249b1b3466527b5d8f3e3a11012930eb737a3efdac63ea98dc24a6adc26a343ae81d5a2fe990d9d0a99efabc5ef184275ba64716b5203058ce15',
  'ADMIN-001',
  'admin'
);