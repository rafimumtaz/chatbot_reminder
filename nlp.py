import re
from datetime import datetime, timedelta, time
import dateparser

DEFAULT_TIME = time(8, 0)  # default jam jika tidak disebut

def parse_reminder_text(text: str, now: datetime | None = None):
    """
    Ekstrak reminder dari teks bahasa Indonesia.
    Deteksi heuristik:
    - 'minggu depan' -> sekarang + 7 hari
    - 'besok' -> sekarang + 1 hari
    - 'hari ini' -> sekarang
    - jam eksplisit: "jam 10", "jam 14:30"
    - judul: kata setelah 'tugas'
    """
    if now is None:
        now = datetime.now()

    text_lower = text.lower()

    # ----------------- DETEKSI HEURISTIK -----------------
    if "minggu depan" in text_lower:
        dt = now + timedelta(days=7)
    elif "besok" in text_lower:
        dt = now + timedelta(days=1)
    elif "hari ini" in text_lower:
        dt = now
    else:
        # fallback ke dateparser
        dt = dateparser.parse(
            text,
            languages=['id'],
            settings={'PREFER_DATES_FROM': 'future'}
        )
        if not dt:
            dt = now + timedelta(days=7)  # default jika tidak bisa parse

    # ----------------- EKSTRAK JAM -----------------
    jam_match = re.search(r'jam\s*(\d{1,2})(?::(\d{2}))?', text_lower)
    if jam_match:
        h = int(jam_match.group(1))
        m = int(jam_match.group(2)) if jam_match.group(2) else 0
        jam_deadline = time(h, m)
    else:
        # gunakan jam dari dt jika ada, jika tidak pakai default
        jam_deadline = dt.time() if dt.time() != datetime.min.time() else DEFAULT_TIME

    tanggal_deadline = dt.date()

    # ----------------- EKSTRAK JUDUL -----------------
    tugas_match = re.search(r'tugas\s+([^,.\n]+)', text_lower)
    if tugas_match:
        judul = ('Tugas ' + tugas_match.group(1)).strip().capitalize()
    else:
        judul = text.strip().capitalize()

    return {
        "judul": judul,
        "deskripsi": text,
        "tanggal_deadline": tanggal_deadline,
        "jam_deadline": jam_deadline,
    }
