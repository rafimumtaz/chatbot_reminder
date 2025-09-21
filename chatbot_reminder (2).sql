-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Waktu pembuatan: 16 Sep 2025 pada 16.23
-- Versi server: 10.4.32-MariaDB
-- Versi PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `chatbot_reminder`
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
-- Struktur dari tabel `kelas`
--

CREATE TABLE `kelas` (
  `id_kelas` int(11) NOT NULL,
  `nama_kelas` varchar(100) NOT NULL,
  `deskripsi` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

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
(1, 1, 1, 'email', '2025-09-13 15:56:53', 'gagal'),
(2, 1, 2, 'email', '2025-09-13 15:56:53', 'gagal'),
(3, 1, 3, 'email', '2025-09-13 15:56:53', 'gagal'),
(4, 1, 4, 'email', '2025-09-13 15:56:54', 'gagal'),
(5, 1, 5, 'email', '2025-09-13 15:56:54', 'gagal'),
(6, 1, 6, 'email', '2025-09-13 15:56:54', 'gagal'),
(7, 1, 7, 'email', '2025-09-13 15:56:54', 'gagal'),
(8, 1, 8, 'email', '2025-09-13 15:56:54', 'gagal'),
(9, 1, 9, 'email', '2025-09-13 15:56:54', 'gagal'),
(10, 1, 16, 'email', '2025-09-13 15:56:54', 'gagal'),
(11, 1, 17, 'email', '2025-09-13 15:56:54', 'gagal'),
(12, 1, 18, 'email', '2025-09-13 15:56:54', 'gagal'),
(13, 1, 19, 'email', '2025-09-13 16:02:13', 'gagal'),
(14, 1, 10, 'email', '2025-09-13 16:26:10', 'terkirim'),
(15, 1, 11, 'email', '2025-09-13 16:26:13', 'terkirim'),
(16, 1, 12, 'email', '2025-09-13 16:26:14', 'terkirim'),
(17, 1, 13, 'email', '2025-09-13 16:26:16', 'terkirim'),
(18, 1, 14, 'email', '2025-09-13 16:26:18', 'terkirim'),
(19, 1, 15, 'email', '2025-09-13 16:26:21', 'terkirim'),
(20, 1, 20, 'email', '2025-09-13 16:42:15', 'terkirim'),
(21, 1, 21, 'email', '2025-09-13 16:47:20', 'terkirim'),
(22, 1, 22, 'email', '2025-09-13 16:55:33', 'terkirim'),
(23, 1, 23, 'email', '2025-09-13 16:55:35', 'terkirim'),
(24, 1, 24, 'email', '2025-09-13 16:55:37', 'terkirim'),
(25, 1, 25, 'email', '2025-09-15 16:28:55', 'terkirim'),
(26, 2, 26, 'email', '2025-09-15 23:07:27', 'terkirim'),
(27, 2, 28, 'email', '2025-09-16 00:08:34', 'terkirim'),
(28, 2, 27, 'email', '2025-09-16 00:09:37', 'terkirim');

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
(1, 1, 1, 'terkirim'),
(2, 2, 1, 'terkirim'),
(3, 3, 1, 'terkirim'),
(4, 4, 1, 'terkirim'),
(5, 5, 1, 'terkirim'),
(6, 6, 1, 'terkirim'),
(7, 7, 1, 'terkirim'),
(8, 8, 1, 'terkirim'),
(9, 9, 1, 'terkirim'),
(10, 10, 1, 'terkirim'),
(11, 11, 1, 'terkirim'),
(12, 12, 1, 'terkirim'),
(13, 13, 1, 'terkirim'),
(14, 14, 1, 'terkirim'),
(15, 15, 1, 'terkirim'),
(16, 16, 1, 'terkirim'),
(17, 17, 1, 'terkirim'),
(18, 18, 1, 'terkirim'),
(19, 19, 1, 'terkirim'),
(20, 20, 1, 'terkirim'),
(21, 21, 1, 'terkirim'),
(22, 22, 1, 'terkirim'),
(23, 23, 1, 'terkirim'),
(24, 24, 1, 'terkirim'),
(25, 25, 1, 'terkirim'),
(26, 26, 2, 'terkirim'),
(27, 27, 2, 'terkirim'),
(28, 28, 2, 'terkirim');

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
(2, 3, '23-175 AHMAD DHIYAUDDIN', 'ptiutmdio@gmail.com', '$2b$12$SVyrh6dOAkKmXOOOrAU./.xOmoTqoAO4CZO1yabfLdeJvQT1CkN6y', NULL, '2025-09-15 23:05:33', NULL, 1);

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
(1, 1, NULL, 'Tugas matematika jam 11\'', 'ingatkan saya minggu depan saya ada tugas matematika jam 11\'', 'pribadi', '2025-08-23', '12:15:00', 0, 'terkirim', NULL, NULL),
(2, 1, NULL, 'Tugas matematika jam 6', 'ingatkan saya minggu depan saya ada tugas matematika jam 6', 'pribadi', '2025-08-23', '12:15:00', 0, 'terkirim', NULL, NULL),
(3, 1, NULL, 'tugas matematika', '-', 'pribadi', '2025-08-25', '15:00:00', 0, 'terkirim', '2025-08-23 14:57:07', NULL),
(4, 1, NULL, 'tugas matematika', '-', 'pribadi', '2025-08-25', '14:59:00', 0, 'terkirim', '2025-08-23 14:57:36', NULL),
(5, 1, NULL, 'tugas matematika', '-', 'pribadi', '2025-08-26', '15:01:00', 0, 'terkirim', '2025-08-23 14:58:44', NULL),
(6, 1, NULL, 'tugas matematika', '-', 'pribadi', '2025-08-26', '15:30:00', 0, 'terkirim', '2025-08-23 15:28:40', NULL),
(7, 1, NULL, 'tugas matematika', '-', 'pribadi', '2025-08-24', '15:30:00', 0, 'terkirim', '2025-08-23 15:31:54', NULL),
(8, 1, NULL, 'tugas matematika', '-', 'pribadi', '2025-08-24', '15:33:00', 0, 'terkirim', '2025-08-23 15:32:25', NULL),
(9, 1, NULL, 'Tugas matematika jam 10', 'ingatkan saya minggu depan saya ada tugas matematika jam 10', 'pribadi', '2025-09-13', '08:15:00', 0, 'terkirim', NULL, NULL),
(10, 1, NULL, 'Tugas matematika jam 10', 'ingatkan saya minggu depan saya ada tugas matematika jam 10', 'pribadi', '2025-09-20', '10:00:00', 0, 'terkirim', NULL, NULL),
(11, 1, NULL, 'Tugas matematika jam 4', 'ingatkan saya minggu depan saya ada tugas matematika jam 4', 'pribadi', '2025-09-20', '04:00:00', 0, 'terkirim', NULL, NULL),
(12, 1, NULL, 'Tugas matematika jam 4 lewat 15', 'ingatkan saya minggu depan saya ada tugas matematika jam 4 lewat 15', 'pribadi', '2025-09-20', '04:00:00', 0, 'terkirim', NULL, NULL),
(13, 1, NULL, 'Tugas matematika jam 4 lewat 15 menit', 'ingatkan saya minggu depan saya ada tugas matematika jam 4 lewat 15 menit', 'pribadi', '2025-09-20', '04:00:00', 0, 'terkirim', NULL, NULL),
(14, 1, NULL, 'Tugas matematika 04:12', 'ingatkan saya minggu depan saya ada tugas matematika 04:12', 'pribadi', '2025-09-20', '10:45:12', 0, 'terkirim', NULL, NULL),
(15, 1, NULL, 'Tugas matematika jam 04:12', 'ingatkan saya minggu depan saya ada tugas matematika jam 04:12', 'pribadi', '2025-09-20', '04:12:00', 0, 'terkirim', NULL, NULL),
(16, 1, NULL, 'Tugas matematika jam 10', 'ingatkan saya besok saya ada tugas matematika jam 10', 'pribadi', '2025-09-14', '10:00:00', 0, 'terkirim', NULL, NULL),
(17, 1, NULL, 'Tugas matematika jam 10', 'ingatkan saya besok saya ada tugas matematika jam 10', 'pribadi', '2025-09-14', '10:00:00', 0, 'terkirim', NULL, NULL),
(18, 1, NULL, 'Tugas matematika jam 10', 'ingatkan saya besok saya ada tugas matematika jam 10', 'pribadi', '2025-09-14', '10:00:00', 0, 'terkirim', NULL, NULL),
(19, 1, NULL, 'Tugas matematika jam 10', 'ingatkan saya besok saya ada tugas matematika jam 10', 'pribadi', '2025-09-14', '10:00:00', 0, 'terkirim', NULL, NULL),
(20, 1, NULL, 'Tugas matematika jam 10', 'ingatkan saya besok saya ada tugas matematika jam 10', 'pribadi', '2025-09-14', '10:00:00', 0, 'terkirim', NULL, NULL),
(21, 1, NULL, 'Tugas matematika jam 10', 'ingatkan saya besok saya ada tugas matematika jam 10', 'pribadi', '2025-09-14', '10:00:00', 0, 'terkirim', NULL, NULL),
(22, 1, NULL, 'Tugas matematika jam 10', 'ingatkan saya besok saya ada tugas matematika jam 10', 'pribadi', '2025-09-14', '10:00:00', 0, 'terkirim', NULL, NULL),
(23, 1, NULL, 'Tugas matematika jam 10', 'ingatkan saya besok saya ada tugas matematika jam 10', 'pribadi', '2025-09-14', '10:00:00', 0, 'terkirim', NULL, NULL),
(24, 1, NULL, 'Tugas matematika jam 10', 'ingatkan saya besok saya ada tugas matematika jam 10', 'pribadi', '2025-09-14', '10:00:00', 0, 'terkirim', NULL, NULL),
(25, 1, NULL, 'Tugas matematika jam 10', 'Ingatkan saya besok saya ada tugas matematika jam 10', 'pribadi', '2025-09-16', '10:00:00', 0, 'terkirim', NULL, NULL),
(26, 2, NULL, 'Tugas matematika jam 10', 'Ingatkan saya besok saya ada tugas matematika jam 10', 'pribadi', '2025-09-16', '10:00:00', 0, 'terkirim', NULL, NULL),
(27, 2, NULL, 'Menggunakan Seragam Pramuka', 'Besok saya harus menggunakan seragam pramuka', 'pribadi', '2025-09-17', '08:30:00', 0, 'terkirim', NULL, NULL),
(28, 2, NULL, 'Mengajar Kelas Matematika', 'Mengajar kelas matematika', 'pribadi', '2024-01-26', '08:15:00', 0, 'terkirim', NULL, NULL);

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
(22, 2, 'tambah_pengingat', 'Chatbot: Mengajar Kelas Matematika', NULL);

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
-- Indexes for dumped tables
--

--
-- Indeks untuk tabel `anggota_kelas`
--
ALTER TABLE `anggota_kelas`
  ADD PRIMARY KEY (`id_anggota_kelas`),
  ADD KEY `id_kelas` (`id_kelas`),
  ADD KEY `id_pengguna` (`id_pengguna`);

--
-- Indeks untuk tabel `arsip_pengingat`
--
ALTER TABLE `arsip_pengingat`
  ADD PRIMARY KEY (`id_arsip`),
  ADD KEY `id_pengingat` (`id_pengingat`);

--
-- Indeks untuk tabel `kelas`
--
ALTER TABLE `kelas`
  ADD PRIMARY KEY (`id_kelas`);

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
  MODIFY `id_anggota_kelas` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `arsip_pengingat`
--
ALTER TABLE `arsip_pengingat`
  MODIFY `id_arsip` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `kelas`
--
ALTER TABLE `kelas`
  MODIFY `id_kelas` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `lampiran_pengingat`
--
ALTER TABLE `lampiran_pengingat`
  MODIFY `id_lampiran` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `notifikasi`
--
ALTER TABLE `notifikasi`
  MODIFY `id_notifikasi` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=29;

--
-- AUTO_INCREMENT untuk tabel `penerima_pengingat`
--
ALTER TABLE `penerima_pengingat`
  MODIFY `id_penerima` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=29;

--
-- AUTO_INCREMENT untuk tabel `pengguna`
--
ALTER TABLE `pengguna`
  MODIFY `id_pengguna` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT untuk tabel `pengingat`
--
ALTER TABLE `pengingat`
  MODIFY `id_pengingat` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=29;

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
  MODIFY `id_aktivitas` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=23;

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
  ADD CONSTRAINT `anggota_kelas_ibfk_1` FOREIGN KEY (`id_kelas`) REFERENCES `kelas` (`id_kelas`),
  ADD CONSTRAINT `anggota_kelas_ibfk_2` FOREIGN KEY (`id_pengguna`) REFERENCES `pengguna` (`id_pengguna`);

--
-- Ketidakleluasaan untuk tabel `arsip_pengingat`
--
ALTER TABLE `arsip_pengingat`
  ADD CONSTRAINT `arsip_pengingat_ibfk_1` FOREIGN KEY (`id_pengingat`) REFERENCES `pengingat` (`id_pengingat`);

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
  ADD CONSTRAINT `notifikasi_ibfk_2` FOREIGN KEY (`id_pengingat`) REFERENCES `pengingat` (`id_pengingat`);

--
-- Ketidakleluasaan untuk tabel `penerima_pengingat`
--
ALTER TABLE `penerima_pengingat`
  ADD CONSTRAINT `penerima_pengingat_ibfk_1` FOREIGN KEY (`id_pengingat`) REFERENCES `pengingat` (`id_pengingat`),
  ADD CONSTRAINT `penerima_pengingat_ibfk_2` FOREIGN KEY (`id_pengguna`) REFERENCES `pengguna` (`id_pengguna`);

--
-- Ketidakleluasaan untuk tabel `pengguna`
--
ALTER TABLE `pengguna`
  ADD CONSTRAINT `pengguna_ibfk_1` FOREIGN KEY (`id_peran`) REFERENCES `peran` (`id_peran`);

--
-- Ketidakleluasaan untuk tabel `pengingat`
--
ALTER TABLE `pengingat`
  ADD CONSTRAINT `pengingat_ibfk_1` FOREIGN KEY (`id_pembuat`) REFERENCES `pengguna` (`id_pengguna`),
  ADD CONSTRAINT `pengingat_ibfk_2` FOREIGN KEY (`id_kelas`) REFERENCES `kelas` (`id_kelas`);

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
