from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Time, Enum, ForeignKey, Text
import enum
from database import Base

Base = declarative_base()

class StatusKirim(enum.Enum):
    terkirim = "terkirim"
    gagal = "gagal"

class MetodeNotif(enum.Enum):
    email = "email"
    

class Peran(Base):
    __tablename__ = "peran"
    id_peran = Column(Integer, primary_key=True, autoincrement=True)
    nama_peran = Column(String(50), nullable=False)

class Pengguna(Base):
    __tablename__ = "pengguna"
    id_pengguna = Column(Integer, primary_key=True, index=True)
    id_peran = Column(Integer, ForeignKey("peran.id_peran"))
    nama_lengkap = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    kata_sandi_hash = Column(String(255), nullable=True) # Dibuat nullable=True untuk Google Login
    
    
    # Tambahkan kolom 'verifikasi_email' di sini
    verifikasi_email = Column(Boolean, default=False)

class Kelas(Base):
    __tablename__ = "kelas"
    id_kelas = Column(Integer, primary_key=True, autoincrement=True)
    nama_kelas = Column(String(100), nullable=False)
    deskripsi = Column(Text)

class AnggotaKelas(Base):
    __tablename__ = "anggota_kelas"
    id_anggota_kelas = Column(Integer, primary_key=True, autoincrement=True)
    id_kelas = Column(Integer, ForeignKey("kelas.id_kelas"), nullable=False)
    id_pengguna = Column(Integer, ForeignKey("pengguna.id_pengguna"), nullable=False)

class Pengingat(Base):
    __tablename__ = "pengingat"
    id_pengingat = Column(Integer, primary_key=True, autoincrement=True)
    id_pembuat = Column(Integer, ForeignKey("pengguna.id_pengguna"), nullable=False)
    id_kelas = Column(Integer, ForeignKey("kelas.id_kelas"))
    judul = Column(String(200), nullable=False)
    deskripsi = Column(Text)
    tipe = Column(String(50))
    tanggal_deadline = Column(Date)
    jam_deadline = Column(Time)
    berulang = Column(Boolean, default=False)
    status_pengiriman = Column(Enum(StatusKirim), default=StatusKirim.terkirim)
    dibuat_pada = Column(DateTime)
    diubah_pada = Column(DateTime)

class PenerimaPengingat(Base):
    __tablename__ = "penerima_pengingat"
    id_penerima = Column(Integer, primary_key=True, autoincrement=True)
    id_pengingat = Column(Integer, ForeignKey("pengingat.id_pengingat"), nullable=False)
    id_pengguna = Column(Integer, ForeignKey("pengguna.id_pengguna"), nullable=False)
    status_pengiriman = Column(Enum(StatusKirim), default=StatusKirim.terkirim)

class LampiranPengingat(Base):
    __tablename__ = "lampiran_pengingat"
    id_lampiran = Column(Integer, primary_key=True, autoincrement=True)
    id_pengingat = Column(Integer, ForeignKey("pengingat.id_pengingat"), nullable=False)
    file_path = Column(String(255), nullable=False)

class Tag(Base):
    __tablename__ = "tag"
    id_tag = Column(Integer, primary_key=True, autoincrement=True)
    nama_tag = Column(String(50), nullable=False)

class PengingatTag(Base):
    __tablename__ = "pengingat_tag"
    id_pengingat = Column(Integer, ForeignKey("pengingat.id_pengingat"), primary_key=True)
    id_tag = Column(Integer, ForeignKey("tag.id_tag"), primary_key=True)

class SesiChatbot(Base):
    __tablename__ = "sesi_chatbot"
    id_sesi = Column(Integer, primary_key=True, autoincrement=True)
    id_pengguna = Column(Integer, ForeignKey("pengguna.id_pengguna"), nullable=False)
    waktu_mulai = Column(DateTime)

class PesanChatbot(Base):
    __tablename__ = "pesan_chatbot"
    id_pesan = Column(Integer, primary_key=True, autoincrement=True)
    id_sesi = Column(Integer, ForeignKey("sesi_chatbot.id_sesi"), nullable=False)
    pengirim = Column(Enum("user","bot", name="enum_pengirim"))
    isi = Column(Text, nullable=False)
    waktu_kirim = Column(DateTime)

class Notifikasi(Base):
    __tablename__ = "notifikasi"
    id_notifikasi = Column(Integer, primary_key=True, autoincrement=True)
    id_pengguna = Column(Integer, ForeignKey("pengguna.id_pengguna"), nullable=False)
    id_pengingat = Column(Integer, ForeignKey("pengingat.id_pengingat"), nullable=False)
    metode = Column(Enum(MetodeNotif), nullable=False)
    waktu_kirim = Column(DateTime)
    status = Column(Enum(StatusKirim), default=StatusKirim.terkirim)

class RiwayatAktivitas(Base):
    __tablename__ = "riwayat_aktivitas"
    id_aktivitas = Column(Integer, primary_key=True, autoincrement=True)
    id_pengguna = Column(Integer, ForeignKey("pengguna.id_pengguna"), nullable=False)
    jenis_aktivitas = Column(String(100), nullable=False)
    deskripsi = Column(Text)
    waktu = Column(DateTime)

class RiwayatPengingat(Base):
    __tablename__ = "riwayat_pengingat"
    id_riwayat = Column(Integer, primary_key=True, autoincrement=True)
    id_pengingat = Column(Integer, ForeignKey("pengingat.id_pengingat"), nullable=False)
    aksi = Column(Enum("ditambah","diubah","dihapus", name="enum_aksi_pengingat"), nullable=False)
    keterangan = Column(Text)
    waktu = Column(DateTime)

class ArsipPengingat(Base):
    __tablename__ = "arsip_pengingat"
    id_arsip = Column(Integer, primary_key=True, autoincrement=True)
    id_pengingat = Column(Integer, ForeignKey("pengingat.id_pengingat"), nullable=False)
    diarsipkan_pada = Column(DateTime)
