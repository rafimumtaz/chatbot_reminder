# Menyisipkan role default: admin, guru, siswa
from database import SessionLocal, engine
from models import Peran

with SessionLocal() as db:
    for r in ["admin","guru","siswa"]:
        if not db.query(Peran).filter(Peran.nama_peran==r).first():
            db.add(Peran(nama_peran=r))
    db.commit()
print("Seed peran selesai.")
