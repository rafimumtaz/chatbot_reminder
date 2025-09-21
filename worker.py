import os
from datetime import datetime, timedelta, time
import pytz

from sqlalchemy.orm import Session
from database import SessionLocal
from models import Pengingat, PenerimaPengingat, Notifikasi, MetodeNotif, StatusKirim, Pengguna

from reminder import send_email  # pastikan ini memanggil SendGrid
from dotenv import load_dotenv

load_dotenv()
TZ = pytz.timezone(os.getenv("TIMEZONE", "Asia/Jakarta"))

# Jam pengiriman H-1
SEND_HOUR = 16
SEND_MINUTE = 15

def h_minus_one_send_time(tanggal_deadline, jam_deadline):
    """
    Hitung waktu H-1 pukul 19:00 lokal
    """
    dt_deadline = datetime.combine(tanggal_deadline, jam_deadline)
    dt_deadline_local = TZ.localize(dt_deadline)
    dt_send = dt_deadline_local - timedelta(days=1)
    dt_send = dt_send.replace(hour=SEND_HOUR, minute=SEND_MINUTE, second=0, microsecond=0)
    return dt_send

def process_notifications():
    now_local = datetime.now(TZ)

    with SessionLocal() as db:
        # Ambil semua penerima pengingat
        q = db.query(PenerimaPengingat, Pengingat, Pengguna)\
            .join(Pengingat, PenerimaPengingat.id_pengingat == Pengingat.id_pengingat)\
            .join(Pengguna, PenerimaPengingat.id_pengguna == Pengguna.id_pengguna)

        for penerima, pengingat, user in q.all():
            if not pengingat.tanggal_deadline or not pengingat.jam_deadline:
                continue

            # send_time = h_minus_one_send_time(pengingat.tanggal_deadline, pengingat.jam_deadline)
            send_time = now_local

            # Hanya kirim jika sekarang >= send_time dan notifikasi belum ada
            if now_local >= send_time:
                already = db.query(Notifikasi).filter(
                    Notifikasi.id_pengguna == user.id_pengguna,
                    Notifikasi.id_pengingat == pengingat.id_pengingat,
                    Notifikasi.metode == MetodeNotif.email
                ).first()
                if already:
                    continue

                # Kirim email
                subject = f"[Pengingat H-1] {pengingat.judul}"
                deadline_str = f"{pengingat.tanggal_deadline} {pengingat.jam_deadline}"
                body = f"""
                <h3>Pengingat Tugas</h3>
                <p>Halo {user.nama_lengkap},</p>
                <p>Ini pengingat H-1 untuk: <b>{pengingat.judul}</b></p>
                <p>Deskripsi: {pengingat.deskripsi or '-'}<br/>
                Deadline: {deadline_str}</p>
                """

                try:
                    send_email(user.email, subject, body)
                    status = StatusKirim.terkirim
                    print(f"Email terkirim ke {user.email} - {pengingat.judul}")
                except Exception as e:
                    print(f"Email gagal ke {user.email} - {e}")
                    status = StatusKirim.gagal

                notif = Notifikasi(
                    id_pengguna=user.id_pengguna,
                    id_pengingat=pengingat.id_pengingat,
                    metode=MetodeNotif.email,
                    waktu_kirim=datetime.now(TZ).replace(tzinfo=None),
                    status=status
                )
                db.add(notif)
                db.commit()

if __name__ == "__main__":
    print("Worker H-1 email reminder dimulai...")
    import schedule
    import time

    # Jadwalkan setiap menit cek pengingat H-1
    schedule.every(1).minutes.do(process_notifications)

    while True:
        try:
            schedule.run_pending()
        except Exception as e:
            print("Error worker loop:", e)
        time.sleep(10)
