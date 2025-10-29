-- phpMyAdmin SQL Dump
-- version 5.2.3
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Waktu pembuatan: 27 Okt 2025 pada 01.22
-- Versi server: 10.3.39-MariaDB
-- Versi PHP: 7.2.24

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Basis data: `chatbot_reminder`
--

-- --------------------------------------------------------

--
-- Struktur dari tabel `anggota_kelas`
--

CREATE TABLE `anggota_kelas` (
  `id_anggota_kelas` int(11) NOT NULL,
  `id_kelas` int(11) NOT NULL,
  `id_pengguna` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `anggota_kelas`
--

INSERT INTO `anggota_kelas` (`id_anggota_kelas`, `id_kelas`, `id_pengguna`) VALUES
(9, 3, 1),
(7, 3, 2),
(10, 4, 1),
(14, 6, 6),
(16, 6, 7);

-- --------------------------------------------------------

--
-- Struktur dari tabel `arsip_pengingat`
--

CREATE TABLE `arsip_pengingat` (
  `id_arsip` int(11) NOT NULL,
  `id_pengingat` int(11) NOT NULL,
  `diarsipkan_pada` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Struktur dari tabel `jadwal_pelajaran`
--

CREATE TABLE `jadwal_pelajaran` (
  `id_jadwal` int(11) NOT NULL,
  `id_pengguna` int(11) NOT NULL,
  `hari` enum('senin','selasa','rabu','kamis','jumat','sabtu','minggu') NOT NULL,
  `nama_pelajaran` varchar(100) NOT NULL,
  `jam_mulai` time NOT NULL,
  `jam_selesai` time NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `jadwal_pelajaran`
--

INSERT INTO `jadwal_pelajaran` (`id_jadwal`, `id_pengguna`, `hari`, `nama_pelajaran`, `jam_mulai`, `jam_selesai`) VALUES
(5, 2, 'senin', 'Matematika', '08:00:00', '09:00:00'),
(7, 2, 'senin', 'matematika', '08:00:00', '09:00:00'),
(8, 2, 'rabu', 'ipa', '08:00:00', '09:00:00'),
(9, 2, 'jumat', 'ipa', '08:00:00', '09:00:00'),
(11, 7, 'selasa', 'pelajaran Matematika', '08:00:00', '09:00:00'),
(12, 7, 'senin', 'IPA', '09:15:00', '10:15:00');

-- --------------------------------------------------------

--
-- Struktur dari tabel `kelas`
--

CREATE TABLE `kelas` (
  `id_kelas` int(11) NOT NULL,
  `nama_kelas` varchar(100) NOT NULL,
  `wali_kelas` varchar(100) NOT NULL,
  `deskripsi` text DEFAULT NULL,
  `id_pembuat` int(11) NOT NULL,
  `kode_kelas` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `kelas`
--

INSERT INTO `kelas` (`id_kelas`, `nama_kelas`, `wali_kelas`, `deskripsi`, `id_pembuat`, `kode_kelas`) VALUES
(3, 'Kelas 12-9', 'Ibu deni', 'Kelas informatika', 2, '67F27E'),
(4, '11-9', 'Ibu deni', 'kelas tataboga', 2, 'BEF349'),
(6, 'Kelas Metpen', 'Hajjid', 'ini adalah kelas metode penelitian', 6, '44208E');

-- --------------------------------------------------------

--
-- Struktur dari tabel `lampiran_pengingat`
--

CREATE TABLE `lampiran_pengingat` (
  `id_lampiran` int(11) NOT NULL,
  `id_pengingat` int(11) NOT NULL,
  `file_path` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Struktur dari tabel `notifikasi`
--

CREATE TABLE `notifikasi` (
  `id_notifikasi` int(11) NOT NULL,
  `id_pengguna` int(11) NOT NULL,
  `id_pengingat` int(11) NOT NULL,
  `metode` enum('email','whatsapp') NOT NULL,
  `waktu_kirim` datetime DEFAULT current_timestamp(),
  `status` enum('terkirim','gagal') DEFAULT 'terkirim'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `notifikasi`
--

INSERT INTO `notifikasi` (`id_notifikasi`, `id_pengguna`, `id_pengingat`, `metode`, `waktu_kirim`, `status`) VALUES
(92, 2, 37, 'email', '2025-10-12 11:33:19', 'terkirim'),
(93, 2, 38, 'email', '2025-10-12 11:33:19', 'terkirim'),
(94, 2, 39, 'email', '2025-10-12 11:33:20', 'terkirim'),
(95, 1, 40, 'email', '2025-10-12 11:33:21', 'terkirim'),
(96, 2, 40, 'email', '2025-10-12 11:33:21', 'terkirim'),
(97, 2, 41, 'email', '2025-10-12 11:33:22', 'terkirim'),
(98, 1, 42, 'email', '2025-10-12 11:33:23', 'terkirim'),
(99, 2, 43, 'email', '2025-10-12 11:33:23', 'terkirim'),
(100, 1, 44, 'email', '2025-10-12 11:33:24', 'terkirim'),
(101, 1, 45, 'email', '2025-10-12 11:33:25', 'terkirim'),
(102, 1, 46, 'email', '2025-10-12 11:33:25', 'terkirim'),
(103, 7, 48, 'email', '2025-10-15 13:01:42', 'terkirim'),
(107, 7, 51, 'email', '2025-10-15 13:45:49', 'terkirim'),
(108, 7, 52, 'email', '2025-10-15 13:46:50', 'terkirim'),
(109, 6, 53, 'email', '2025-10-15 13:58:52', 'terkirim'),
(110, 7, 54, 'email', '2025-10-15 14:00:53', 'terkirim');

-- --------------------------------------------------------

--
-- Struktur dari tabel `penerima_pengingat`
--

CREATE TABLE `penerima_pengingat` (
  `id_penerima` int(11) NOT NULL,
  `id_pengingat` int(11) NOT NULL,
  `id_pengguna` int(11) NOT NULL,
  `status_pengiriman` enum('terkirim','gagal') DEFAULT 'terkirim'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `penerima_pengingat`
--

INSERT INTO `penerima_pengingat` (`id_penerima`, `id_pengingat`, `id_pengguna`, `status_pengiriman`) VALUES
(40, 37, 2, 'terkirim'),
(41, 38, 2, 'terkirim'),
(42, 39, 2, 'terkirim'),
(43, 40, 1, 'terkirim'),
(44, 40, 2, 'terkirim'),
(45, 41, 2, 'terkirim'),
(46, 42, 1, 'terkirim'),
(47, 43, 2, 'terkirim'),
(48, 44, 1, 'terkirim'),
(49, 45, 1, 'terkirim'),
(50, 46, 1, 'terkirim'),
(52, 48, 7, 'terkirim'),
(56, 51, 7, 'terkirim'),
(57, 52, 7, 'terkirim'),
(58, 53, 6, 'terkirim'),
(59, 54, 7, 'terkirim'),
(65, 57, 6, 'terkirim');

-- --------------------------------------------------------

--
-- Struktur dari tabel `pengguna`
--

CREATE TABLE `pengguna` (
  `id_pengguna` int(11) NOT NULL,
  `id_peran` int(11) NOT NULL,
  `nama_lengkap` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `kata_sandi_hash` varchar(255) DEFAULT NULL,
  `foto_profil` varchar(255) DEFAULT NULL,
  `tanggal_dibuat` datetime DEFAULT current_timestamp(),
  `terakhir_login` datetime DEFAULT NULL,
  `verifikasi_email` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `pengguna`
--

INSERT INTO `pengguna` (`id_pengguna`, `id_peran`, `nama_lengkap`, `email`, `kata_sandi_hash`, `foto_profil`, `tanggal_dibuat`, `terakhir_login`, `verifikasi_email`) VALUES
(1, 3, 'dhyos', 'drp022020@gmail.com', '$2b$12$qmxayiu0q..A01FmGtFsFOE1AF.OI5FvKMiBvES0.QSuVtAt46rlO', NULL, NULL, NULL, 0),
(2, 2, '23-175 AHMAD DHIYAUDDIN', 'ptiutmdio@gmail.com', '$2b$12$SVyrh6dOAkKmXOOOrAU./.xOmoTqoAO4CZO1yabfLdeJvQT1CkN6y', NULL, '2025-09-15 23:05:33', NULL, 1),
(3, 3, 'AHMAD DHIYAUDDIN-PURE', 'dpr012020@gmail.com', NULL, NULL, '2025-09-17 10:24:49', NULL, 1),
(4, 3, 'chatbot reminder', 'chatbotremind@gmail.com', NULL, NULL, '2025-09-26 10:23:45', NULL, 1),
(5, 3, 'dhass', 'dpr042020@gmail.com', '$2b$12$ANzfoE33WJ58keL6Rj71ie.bKRVcPRDauVjp5NIn71fhar/AWpn6q', NULL, '2025-10-02 14:19:05', NULL, 1),
(6, 2, '23-078 HAJJID RAFI MUMTAZ', 'rafimumtaz86@gmail.com', NULL, NULL, '2025-10-15 12:25:20', NULL, 1),
(7, 3, '23-078 HAJJID RAFI MUMTAZ', '230411100078@student.trunojoyo.ac.id', NULL, NULL, '2025-10-15 12:28:21', NULL, 1);

--
-- Trigger `pengguna`
--
DELIMITER $$
CREATE TRIGGER `set_guru_role_before_insert` BEFORE INSERT ON `pengguna` FOR EACH ROW BEGIN
    -- Cek jika email baru berakhiran dengan @guru.belajar.id
    IF NEW.email LIKE '%@guru.belajar.id' THEN
        -- Set id_peran menjadi 2 (ID untuk peran Guru)
        SET NEW.id_peran = 2;
    END IF;
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Struktur dari tabel `pengingat`
--

CREATE TABLE `pengingat` (
  `id_pengingat` int(11) NOT NULL,
  `id_pembuat` int(11) NOT NULL,
  `id_kelas` int(11) DEFAULT NULL,
  `judul` varchar(200) NOT NULL,
  `deskripsi` text DEFAULT NULL,
  `tipe` varchar(50) DEFAULT NULL,
  `tanggal_deadline` date DEFAULT NULL,
  `jam_deadline` time DEFAULT NULL,
  `berulang` tinyint(1) DEFAULT 0,
  `status_pengiriman` enum('terkirim','gagal') DEFAULT 'terkirim',
  `dibuat_pada` datetime DEFAULT current_timestamp(),
  `diubah_pada` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `pengingat`
--

INSERT INTO `pengingat` (`id_pengingat`, `id_pembuat`, `id_kelas`, `judul`, `deskripsi`, `tipe`, `tanggal_deadline`, `jam_deadline`, `berulang`, `status_pengiriman`, `dibuat_pada`, `diubah_pada`) VALUES
(37, 2, NULL, 'Tugas Matematika', 'ingatkan saya besok ada tugas matematika untuk kelas 12-9', 'kelas 12-9', '2025-10-01', '07:00:00', 0, 'terkirim', NULL, NULL),
(38, 2, NULL, 'Tugas Matematika', 'ingatkan saya besok ada tugas matematika untuk kelas 12-9', 'kelas 12-9', '2025-10-05', '07:00:00', 0, 'terkirim', NULL, NULL),
(39, 2, NULL, 'Tugas Matematika', 'ingatkan saya besok ada tugas matematika untuk kelas 12-9', 'kelas 12-9', '2025-10-09', '07:00:00', 0, 'terkirim', NULL, NULL),
(40, 2, 3, 'Tugas Matematika', 'ingatkan saya besok ada tugas matematika untuk kelas 12-9', 'kelas 12-9', '2025-10-09', '07:00:00', 0, 'terkirim', NULL, NULL),
(41, 2, NULL, 'Tugas Matematika', 'ingatkan saya besok ada tugas matematika untuk kelas 11-9', 'pribadi', '2025-10-09', '07:00:00', 0, 'terkirim', NULL, NULL),
(42, 2, 4, 'tugas matematika', 'ingatkan saya besok ada tugas matematika untuk 11-9', '11-9', '2025-10-09', '07:00:00', 0, 'terkirim', NULL, NULL),
(43, 2, NULL, 'Tugas Matematika', 'Ada tugas matematika untuk kelas 11-9', 'Pribadi', '2025-10-09', '07:00:00', 0, 'terkirim', NULL, NULL),
(44, 2, 4, 'Tugas Matematika', 'ingatkan saya besok ada tugas matematika untuk kelas 11-9', '11-9', '2025-10-09', '07:00:00', 0, 'terkirim', NULL, NULL),
(45, 2, 4, 'Tugas IPA', 'ingatkan saya besok ada tugas ipa untuk kelas 11-9', '11-9', '2025-10-09', '07:00:00', 0, 'terkirim', NULL, NULL),
(46, 1, 4, 'Tugas IPA', 'ingatkan saya besok ada tugas ipa untuk kelas 11-9', '11-9', '2025-10-08', '07:00:00', 0, 'terkirim', NULL, NULL),
(48, 7, NULL, 'Tugas IPA', 'tolong ingatkan saya besok ada tugas Matematika deadline jam 15:30 WIB', 'Pribadi', '2025-10-16', '15:30:00', 0, 'terkirim', NULL, NULL),
(51, 7, NULL, 'Tugas Metpen', 'tolong ingatkan saya besok ada tugas metpen deadline jam 16:00', 'Pribadi', '2025-10-15', '16:00:00', 0, 'terkirim', NULL, NULL),
(52, 7, NULL, 'Tugas Metpen', 'tolong ingatkan saya besok ada tugas metpen deadline jam 16:00', 'Pribadi', '2025-10-16', '16:00:00', 0, 'terkirim', NULL, NULL),
(53, 6, NULL, 'Tugas Biologi', 'tolong ingatkan saya besok ada tugas biologi deadline jam 12:00', 'Pribadi', '2025-10-15', '12:00:00', 0, 'terkirim', NULL, NULL),
(54, 7, NULL, 'Mengenakan Seragam Pramuka', 'tolong ingatkan saya besok saya harus mengenakan seragam pramuka', 'Pribadi', '2025-10-16', '07:00:00', 0, 'terkirim', NULL, NULL),
(57, 6, 6, 'Besok Akan ada ujian tertulis', 'besok akan ada ujian tertulis, silahkan siapkan alat tulis dan kertas hvs A4', 'Pengumuman', '2025-10-22', '19:35:00', 0, 'terkirim', NULL, NULL);

--
-- Trigger `pengingat`
--
DELIMITER $$
CREATE TRIGGER `log_delete_pengingat_rev` AFTER DELETE ON `pengingat` FOR EACH ROW BEGIN
    INSERT INTO riwayat_aktivitas (id_pengguna, jenis_aktivitas, deskripsi)
    VALUES (
        OLD.id_pembuat,
        'Hapus Pengingat',
        CONCAT('Pengingat dengan judul "', OLD.judul, '" (ID: ', OLD.id_pengingat, ') telah dihapus.')
    );
END
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `log_tambah_pengingat` AFTER INSERT ON `pengingat` FOR EACH ROW BEGIN
    INSERT INTO riwayat_aktivitas (id_pengguna, jenis_aktivitas, deskripsi)
    VALUES (
        NEW.id_pembuat,
        'tambah pengingat',
        CONCAT('Judul pengingat (ID: ', NEW.id_pengingat, ') "', NEW.judul, '" ditambahkan')
    );
END
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `log_update_pengingat_rev` AFTER UPDATE ON `pengingat` FOR EACH ROW BEGIN
    INSERT INTO riwayat_aktivitas (id_pengguna, jenis_aktivitas, deskripsi)
    VALUES (
        OLD.id_pembuat,
        'Update Pengingat',
        CONCAT('Judul pengingat (ID: ', OLD.id_pengingat, ') "', OLD.judul, '" sudah di di update')
    );
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Struktur dari tabel `pengingat_tag`
--

CREATE TABLE `pengingat_tag` (
  `id_pengingat` int(11) NOT NULL,
  `id_tag` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Struktur dari tabel `peran`
--

CREATE TABLE `peran` (
  `id_peran` int(11) NOT NULL,
  `nama_peran` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `peran`
--

INSERT INTO `peran` (`id_peran`, `nama_peran`) VALUES
(1, 'admin'),
(2, 'guru'),
(3, 'siswa');

-- --------------------------------------------------------

--
-- Struktur dari tabel `pesan_chatbot`
--

CREATE TABLE `pesan_chatbot` (
  `id_pesan` int(11) NOT NULL,
  `id_sesi` int(11) NOT NULL,
  `pengirim` enum('user','bot') NOT NULL,
  `isi` text NOT NULL,
  `waktu_kirim` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Struktur dari tabel `riwayat_aktivitas`
--

CREATE TABLE `riwayat_aktivitas` (
  `id_aktivitas` int(11) NOT NULL,
  `id_pengguna` int(11) NOT NULL,
  `jenis_aktivitas` varchar(100) NOT NULL,
  `deskripsi` text DEFAULT NULL,
  `waktu` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `riwayat_aktivitas`
--

INSERT INTO `riwayat_aktivitas` (`id_aktivitas`, `id_pengguna`, `jenis_aktivitas`, `deskripsi`, `waktu`) VALUES
(1, 1, 'tambah_pengingat', 'Chatbot: Tugas matematika jam 11\'', NULL),
(2, 1, 'tambah_pengingat', 'Chatbot: Tugas matematika jam 6', NULL),
(3, 1, 'tambah_pengingat', 'Chatbot: Tugas matematika jam 10', NULL),
(4, 1, 'tambah_pengingat', 'Chatbot: Tugas matematika jam 10', NULL),
(5, 1, 'tambah_pengingat', 'Chatbot: Tugas matematika jam 4', NULL),
(6, 1, 'tambah_pengingat', 'Chatbot: Tugas matematika jam 4 lewat 15', NULL),
(7, 1, 'tambah_pengingat', 'Chatbot: Tugas matematika jam 4 lewat 15 menit', NULL),
(8, 1, 'tambah_pengingat', 'Chatbot: Tugas matematika 04:12', NULL),
(9, 1, 'tambah_pengingat', 'Chatbot: Tugas matematika jam 04:12', NULL),
(10, 1, 'tambah_pengingat', 'Chatbot: Tugas matematika jam 10', NULL),
(11, 1, 'tambah_pengingat', 'Chatbot: Tugas matematika jam 10', NULL),
(12, 1, 'tambah_pengingat', 'Chatbot: Tugas matematika jam 10', NULL),
(13, 1, 'tambah_pengingat', 'Chatbot: Tugas matematika jam 10', NULL),
(14, 1, 'tambah_pengingat', 'Chatbot: Tugas matematika jam 10', NULL),
(15, 1, 'tambah_pengingat', 'Chatbot: Tugas matematika jam 10', NULL),
(16, 1, 'tambah_pengingat', 'Chatbot: Tugas matematika jam 10', NULL),
(17, 1, 'tambah_pengingat', 'Chatbot: Tugas matematika jam 10', NULL),
(18, 1, 'tambah_pengingat', 'Chatbot: Tugas matematika jam 10', NULL),
(19, 1, 'tambah_pengingat', 'Chatbot: Tugas matematika jam 10', NULL),
(20, 2, 'tambah_pengingat', 'Chatbot: Tugas matematika jam 10', NULL),
(21, 2, 'tambah_pengingat', 'Chatbot: Menggunakan Seragam Pramuka', NULL),
(22, 2, 'tambah_pengingat', 'Chatbot: Mengajar Kelas Matematika', NULL),
(23, 3, 'tambah_pengingat', 'Chatbot: Menggunakan Baju Tradisional', NULL),
(24, 3, 'tambah_pengingat', 'Chatbot: Memakai Baju Tradisional', NULL),
(25, 1, 'tambah_pengingat', 'Chatbot: Tugas Matematika (11-9)', NULL),
(26, 2, 'tambah_pengingat', 'Chatbot: Tugas IPA (11-9)', NULL),
(27, 2, 'tambah_pengingat', 'Chatbot: Tugas Matematika (11-9)', NULL),
(28, 5, 'tambah_pengingat', 'Chatbot: Tugas Matematika (Pribadi)', NULL),
(29, 2, 'tambah_pengingat', 'Chatbot: Tugas matematika (Pribadi)', NULL),
(30, 2, 'tambah_pengingat', 'Chatbot: Tugas Matematika (Pribadi)', NULL),
(31, 2, 'tambah_pengingat', 'Chatbot: Tugas Matematika (Pribadi)', NULL),
(32, 2, 'tambah_pengingat', 'Chatbot: Tugas Matematika (Pribadi)', NULL),
(33, 2, 'tambah_pengingat', 'Chatbot: Tugas Matematika (Pribadi)', NULL),
(34, 2, 'tambah_pengingat', 'Chatbot: Tugas Matematika (Tujuan: Kelas 12-9)', NULL),
(35, 2, 'tambah_pengingat', 'Chatbot: Tugas Matematika (Tujuan: Pribadi)', NULL),
(36, 2, 'tambah_pengingat', 'Chatbot: tugas matematika (Tujuan: 11-9)', NULL),
(37, 2, 'tambah_pengingat', 'Chatbot: Tugas Matematika (Tujuan: Pribadi)', NULL),
(38, 2, 'tambah_pengingat', 'Chatbot: Tugas Matematika (Tujuan: 11-9)', NULL),
(39, 2, 'tambah_pengingat', 'Chatbot: Tugas IPA (Tujuan: 11-9)', NULL),
(40, 1, 'tambah_pengingat', 'Chatbot: Tugas IPA (Tujuan: 11-9)', NULL),
(41, 2, 'Update Pengingat', 'Judul pengingat (ID: 36) diubah dari \"Tugas Matematika\" menjadi \"Tugas Matematika\".', '2025-10-12 11:55:56'),
(42, 2, 'Hapus Pengingat', 'Pengingat dengan judul \"Tugas Matematika\" (ID: 36) telah dihapus.', '2025-10-12 11:57:50'),
(43, 2, 'tambah_pengingat', 'Chatbot: Tugas IPA (Tujuan: Pribadi)', '2025-10-12 12:02:36'),
(44, 2, 'Update Pengingat', 'Judul pengingat (ID: 47) diubah dari \"Tugas IPA\" menjadi \"Tugas IPA\".', '2025-10-12 12:03:05'),
(45, 2, 'Hapus Pengingat', 'Pengingat dengan judul \"Tugas IPA\" (ID: 47) telah dihapus.', '2025-10-12 12:03:26'),
(46, 2, 'Update Pengingat', 'Judul pengingat (ID: 37) diubah dari \"Tugas Matematika\" menjadi \"Tugas Matematika\".', '2025-10-12 12:21:04'),
(47, 2, 'Update Pengingat', 'Judul pengingat (ID: 37) diubah dari \"Tugas Matematika\" menjadi \"Tugas Matematika\".', '2025-10-12 12:21:33'),
(48, 2, 'Update Pengingat', 'Judul pengingat (ID: 37) \"Tugas Matematika\" sudah di di update \"', '2025-10-12 12:39:30'),
(49, 7, 'tambah pengingat', 'Chatbot: Tugas Matematika (Tujuan: Pribadi)', NULL),
(50, 7, 'tambah pengingat', 'Chatbot: Ujian KELAS KONTOL (Tujuan: KELAS KONTOL)', NULL),
(51, 7, 'tambah pengingat', 'Chatbot: Tugas Matematika (Tujuan: Pribadi)', NULL),
(52, 7, 'Hapus Pengingat', 'Pengingat dengan judul \"Tugas Matematika\" (ID: 50) telah dihapus.', '2025-10-15 13:40:39'),
(53, 7, 'tambah pengingat', 'Chatbot: Tugas Metpen (Tujuan: Pribadi)', NULL),
(54, 7, 'tambah pengingat', 'Chatbot: Tugas Metpen (Tujuan: Pribadi)', NULL),
(55, 7, 'Update Pengingat', 'Judul pengingat (ID: 48) \"Tugas Matematika\" sudah di di update', '2025-10-15 13:51:10'),
(56, 6, 'tambah pengingat', 'Judul pengingat (ID: 53) \"Tugas Biologi\" ditambahkan', '2025-10-15 13:57:52'),
(57, 6, 'tambah pengingat', 'Chatbot: Tugas Biologi (Tujuan: Pribadi)', NULL),
(58, 7, 'tambah pengingat', 'Judul pengingat (ID: 54) \"Mengenakan Seragam Pramuka\" ditambahkan', '2025-10-15 14:00:18'),
(59, 7, 'tambah pengingat', 'Chatbot: Mengenakan Seragam Pramuka (Tujuan: Pribadi)', NULL),
(60, 6, 'tambah pengingat', 'Judul pengingat (ID: 55) \"Ujian Tertulis\" ditambahkan', '2025-10-17 14:28:02'),
(61, 6, 'tambah pengingat', 'Chatbot: Ujian Tertulis (Tujuan: KELAS KONTOL)', NULL),
(62, 6, 'tambah pengingat', 'Judul pengingat (ID: 56) \"Besok ujian\" ditambahkan', '2025-10-19 11:26:42'),
(63, 6, 'Update Pengingat', 'Judul pengingat (ID: 55) \"Ujian Tertulis\" sudah di di update', '2025-10-19 11:46:33'),
(64, 6, 'Update Pengingat', 'Judul pengingat (ID: 56) \"Besok ujian\" sudah di di update', '2025-10-19 11:46:51'),
(65, 6, 'tambah pengingat', 'Judul pengingat (ID: 57) \"Besok Akan ada ujian tertulis\" ditambahkan', '2025-10-22 19:35:47');

-- --------------------------------------------------------

--
-- Struktur dari tabel `riwayat_pengingat`
--

CREATE TABLE `riwayat_pengingat` (
  `id_riwayat` int(11) NOT NULL,
  `id_pengingat` int(11) NOT NULL,
  `aksi` enum('ditambah','diubah','dihapus') NOT NULL,
  `keterangan` text DEFAULT NULL,
  `waktu` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Struktur dari tabel `sesi_chatbot`
--

CREATE TABLE `sesi_chatbot` (
  `id_sesi` int(11) NOT NULL,
  `id_pengguna` int(11) NOT NULL,
  `waktu_mulai` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Struktur dari tabel `tag`
--

CREATE TABLE `tag` (
  `id_tag` int(11) NOT NULL,
  `nama_tag` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Indeks untuk tabel yang dibuang
--

--
-- Indeks untuk tabel `anggota_kelas`
--
ALTER TABLE `anggota_kelas`
  ADD PRIMARY KEY (`id_anggota_kelas`),
  ADD UNIQUE KEY `_kelas_anggota_uc` (`id_kelas`,`id_pengguna`),
  ADD KEY `id_pengguna` (`id_pengguna`);

--
-- Indeks untuk tabel `arsip_pengingat`
--
ALTER TABLE `arsip_pengingat`
  ADD PRIMARY KEY (`id_arsip`),
  ADD KEY `id_pengingat` (`id_pengingat`);

--
-- Indeks untuk tabel `jadwal_pelajaran`
--
ALTER TABLE `jadwal_pelajaran`
  ADD PRIMARY KEY (`id_jadwal`),
  ADD KEY `id_pengguna` (`id_pengguna`);

--
-- Indeks untuk tabel `kelas`
--
ALTER TABLE `kelas`
  ADD PRIMARY KEY (`id_kelas`),
  ADD UNIQUE KEY `kode_kelas` (`kode_kelas`),
  ADD KEY `fk_kelas_pembuat` (`id_pembuat`);

--
-- Indeks untuk tabel `lampiran_pengingat`
--
ALTER TABLE `lampiran_pengingat`
  ADD PRIMARY KEY (`id_lampiran`),
  ADD KEY `id_pengingat` (`id_pengingat`);

--
-- Indeks untuk tabel `notifikasi`
--
ALTER TABLE `notifikasi`
  ADD PRIMARY KEY (`id_notifikasi`),
  ADD KEY `id_pengguna` (`id_pengguna`),
  ADD KEY `id_pengingat` (`id_pengingat`);

--
-- Indeks untuk tabel `penerima_pengingat`
--
ALTER TABLE `penerima_pengingat`
  ADD PRIMARY KEY (`id_penerima`),
  ADD KEY `id_pengingat` (`id_pengingat`),
  ADD KEY `id_pengguna` (`id_pengguna`);

--
-- Indeks untuk tabel `pengguna`
--
ALTER TABLE `pengguna`
  ADD PRIMARY KEY (`id_pengguna`),
  ADD UNIQUE KEY `email` (`email`),
  ADD KEY `id_peran` (`id_peran`);

--
-- Indeks untuk tabel `pengingat`
--
ALTER TABLE `pengingat`
  ADD PRIMARY KEY (`id_pengingat`),
  ADD KEY `id_pembuat` (`id_pembuat`),
  ADD KEY `id_kelas` (`id_kelas`);

--
-- Indeks untuk tabel `pengingat_tag`
--
ALTER TABLE `pengingat_tag`
  ADD PRIMARY KEY (`id_pengingat`,`id_tag`),
  ADD KEY `id_tag` (`id_tag`);

--
-- Indeks untuk tabel `peran`
--
ALTER TABLE `peran`
  ADD PRIMARY KEY (`id_peran`);

--
-- Indeks untuk tabel `pesan_chatbot`
--
ALTER TABLE `pesan_chatbot`
  ADD PRIMARY KEY (`id_pesan`),
  ADD KEY `id_sesi` (`id_sesi`);

--
-- Indeks untuk tabel `riwayat_aktivitas`
--
ALTER TABLE `riwayat_aktivitas`
  ADD PRIMARY KEY (`id_aktivitas`),
  ADD KEY `id_pengguna` (`id_pengguna`);

--
-- Indeks untuk tabel `riwayat_pengingat`
--
ALTER TABLE `riwayat_pengingat`
  ADD PRIMARY KEY (`id_riwayat`),
  ADD KEY `id_pengingat` (`id_pengingat`);

--
-- Indeks untuk tabel `sesi_chatbot`
--
ALTER TABLE `sesi_chatbot`
  ADD PRIMARY KEY (`id_sesi`),
  ADD KEY `id_pengguna` (`id_pengguna`);

--
-- Indeks untuk tabel `tag`
--
ALTER TABLE `tag`
  ADD PRIMARY KEY (`id_tag`);

--
-- AUTO_INCREMENT untuk tabel yang dibuang
--

--
-- AUTO_INCREMENT untuk tabel `anggota_kelas`
--
ALTER TABLE `anggota_kelas`
  MODIFY `id_anggota_kelas` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- AUTO_INCREMENT untuk tabel `arsip_pengingat`
--
ALTER TABLE `arsip_pengingat`
  MODIFY `id_arsip` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `jadwal_pelajaran`
--
ALTER TABLE `jadwal_pelajaran`
  MODIFY `id_jadwal` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT untuk tabel `kelas`
--
ALTER TABLE `kelas`
  MODIFY `id_kelas` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT untuk tabel `lampiran_pengingat`
--
ALTER TABLE `lampiran_pengingat`
  MODIFY `id_lampiran` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `notifikasi`
--
ALTER TABLE `notifikasi`
  MODIFY `id_notifikasi` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=113;

--
-- AUTO_INCREMENT untuk tabel `penerima_pengingat`
--
ALTER TABLE `penerima_pengingat`
  MODIFY `id_penerima` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=66;

--
-- AUTO_INCREMENT untuk tabel `pengguna`
--
ALTER TABLE `pengguna`
  MODIFY `id_pengguna` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT untuk tabel `pengingat`
--
ALTER TABLE `pengingat`
  MODIFY `id_pengingat` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=58;

--
-- AUTO_INCREMENT untuk tabel `peran`
--
ALTER TABLE `peran`
  MODIFY `id_peran` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT untuk tabel `pesan_chatbot`
--
ALTER TABLE `pesan_chatbot`
  MODIFY `id_pesan` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `riwayat_aktivitas`
--
ALTER TABLE `riwayat_aktivitas`
  MODIFY `id_aktivitas` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=66;

--
-- AUTO_INCREMENT untuk tabel `riwayat_pengingat`
--
ALTER TABLE `riwayat_pengingat`
  MODIFY `id_riwayat` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `sesi_chatbot`
--
ALTER TABLE `sesi_chatbot`
  MODIFY `id_sesi` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `tag`
--
ALTER TABLE `tag`
  MODIFY `id_tag` int(11) NOT NULL AUTO_INCREMENT;

--
-- Ketidakleluasaan untuk tabel pelimpahan (Dumped Tables)
--

--
-- Ketidakleluasaan untuk tabel `anggota_kelas`
--
ALTER TABLE `anggota_kelas`
  ADD CONSTRAINT `anggota_kelas_ibfk_1` FOREIGN KEY (`id_kelas`) REFERENCES `kelas` (`id_kelas`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `anggota_kelas_ibfk_2` FOREIGN KEY (`id_pengguna`) REFERENCES `pengguna` (`id_pengguna`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Ketidakleluasaan untuk tabel `arsip_pengingat`
--
ALTER TABLE `arsip_pengingat`
  ADD CONSTRAINT `arsip_pengingat_ibfk_1` FOREIGN KEY (`id_pengingat`) REFERENCES `pengingat` (`id_pengingat`);

--
-- Ketidakleluasaan untuk tabel `jadwal_pelajaran`
--
ALTER TABLE `jadwal_pelajaran`
  ADD CONSTRAINT `jadwal_pelajaran_ibfk_1` FOREIGN KEY (`id_pengguna`) REFERENCES `pengguna` (`id_pengguna`);

--
-- Ketidakleluasaan untuk tabel `kelas`
--
ALTER TABLE `kelas`
  ADD CONSTRAINT `fk_kelas_pembuat` FOREIGN KEY (`id_pembuat`) REFERENCES `pengguna` (`id_pengguna`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Ketidakleluasaan untuk tabel `lampiran_pengingat`
--
ALTER TABLE `lampiran_pengingat`
  ADD CONSTRAINT `lampiran_pengingat_ibfk_1` FOREIGN KEY (`id_pengingat`) REFERENCES `pengingat` (`id_pengingat`);

--
-- Ketidakleluasaan untuk tabel `notifikasi`
--
ALTER TABLE `notifikasi`
  ADD CONSTRAINT `notifikasi_ibfk_1` FOREIGN KEY (`id_pengguna`) REFERENCES `pengguna` (`id_pengguna`),
  ADD CONSTRAINT `notifikasi_ibfk_2` FOREIGN KEY (`id_pengingat`) REFERENCES `pengingat` (`id_pengingat`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Ketidakleluasaan untuk tabel `penerima_pengingat`
--
ALTER TABLE `penerima_pengingat`
  ADD CONSTRAINT `penerima_pengingat_ibfk_1` FOREIGN KEY (`id_pengingat`) REFERENCES `pengingat` (`id_pengingat`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `penerima_pengingat_ibfk_2` FOREIGN KEY (`id_pengguna`) REFERENCES `pengguna` (`id_pengguna`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Ketidakleluasaan untuk tabel `pengguna`
--
ALTER TABLE `pengguna`
  ADD CONSTRAINT `pengguna_ibfk_1` FOREIGN KEY (`id_peran`) REFERENCES `peran` (`id_peran`);

--
-- Ketidakleluasaan untuk tabel `pengingat`
--
ALTER TABLE `pengingat`
  ADD CONSTRAINT `pengingat_ibfk_1` FOREIGN KEY (`id_pembuat`) REFERENCES `pengguna` (`id_pengguna`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `pengingat_ibfk_2` FOREIGN KEY (`id_kelas`) REFERENCES `kelas` (`id_kelas`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Ketidakleluasaan untuk tabel `pengingat_tag`
--
ALTER TABLE `pengingat_tag`
  ADD CONSTRAINT `pengingat_tag_ibfk_1` FOREIGN KEY (`id_pengingat`) REFERENCES `pengingat` (`id_pengingat`),
  ADD CONSTRAINT `pengingat_tag_ibfk_2` FOREIGN KEY (`id_tag`) REFERENCES `tag` (`id_tag`);

--
-- Ketidakleluasaan untuk tabel `pesan_chatbot`
--
ALTER TABLE `pesan_chatbot`
  ADD CONSTRAINT `pesan_chatbot_ibfk_1` FOREIGN KEY (`id_sesi`) REFERENCES `sesi_chatbot` (`id_sesi`);

--
-- Ketidakleluasaan untuk tabel `riwayat_aktivitas`
--
ALTER TABLE `riwayat_aktivitas`
  ADD CONSTRAINT `riwayat_aktivitas_ibfk_1` FOREIGN KEY (`id_pengguna`) REFERENCES `pengguna` (`id_pengguna`);

--
-- Ketidakleluasaan untuk tabel `riwayat_pengingat`
--
ALTER TABLE `riwayat_pengingat`
  ADD CONSTRAINT `riwayat_pengingat_ibfk_1` FOREIGN KEY (`id_pengingat`) REFERENCES `pengingat` (`id_pengingat`);

--
-- Ketidakleluasaan untuk tabel `sesi_chatbot`
--
ALTER TABLE `sesi_chatbot`
  ADD CONSTRAINT `sesi_chatbot_ibfk_1` FOREIGN KEY (`id_pengguna`) REFERENCES `pengguna` (`id_pengguna`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
