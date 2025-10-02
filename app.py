import streamlit as st
import streamlit_authenticator as stauth
from dotenv import load_dotenv
import os
import json
from datetime import date, time, timedelta, datetime
import uuid
import google.generativeai as genai
from streamlit_option_menu import option_menu
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from passlib.hash import bcrypt
from pathlib import Path
from sqlalchemy.exc import IntegrityError

from database import SessionLocal
# Impor model yang dibutuhkan
from models import Pengguna, Peran, Pengingat, PenerimaPengingat, JadwalPelajaran, Hari,Notifikasi, RiwayatAktivitas, Kelas, AnggotaKelas

# Menggunakan Streamlit secrets untuk kredensial
CLIENT_ID = st.secrets["google"]["GOOGLE_CLIENT_ID"]
CLIENT_SECRET = st.secrets["google"]["GOOGLE_CLIENT_SECRET"]

# Inisialisasi Gemini API
genai.configure(api_key=st.secrets["gemini"]["GEMINI_API_KEY"])

# URL callback (redirect URI) harus cocok dengan yang di Google Cloud Console
REDIRECT_URI = "http://localhost:8501/"
SCOPES = ["openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"]

# ------------------------------------------------
# --- AUTH UTILITIES ---
# ------------------------------------------------

def get_user_by_email(db, email):
    return db.query(Pengguna).filter(Pengguna.email == email).first()

def create_user(db, nama, email, password=None, from_google=False):
    role = db.query(Peran).filter(Peran.nama_peran == "siswa").first()
    if not role:
        role = Peran(nama_peran="siswa")
        db.add(role)
        db.commit()
        db.refresh(role)
    
    kata_sandi_hash = bcrypt.hash(password) if password else None

    user = Pengguna(
        id_peran=role.id_peran,
        nama_lengkap=nama,
        email=email,
        kata_sandi_hash=kata_sandi_hash,
        verifikasi_email=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update_password(user_id, old_password, new_password):
    with SessionLocal() as db:
        user = db.query(Pengguna).filter(Pengguna.id_pengguna == user_id).first()
        if not user:
            return False, "Pengguna tidak ditemukan."
        
        if user.kata_sandi_hash is None:
            if old_password:
                return False, "Akun ini tidak memiliki kata sandi lama. Kosongkan kolom kata sandi lama."
        else:
            if not bcrypt.verify(old_password, user.kata_sandi_hash):
                return False, "Kata sandi lama salah."
                
        user.kata_sandi_hash = bcrypt.hash(new_password)
        db.commit()
        return True, "Kata sandi berhasil diubah."

def update_nama(user_id, new_nama):
    with SessionLocal() as db:
        user = db.query(Pengguna).filter(Pengguna.id_pengguna == user_id).first()
        if not user:
            return False, "Pengguna tidak ditemukan."
        
        user.nama_lengkap = new_nama
        db.commit()
        db.refresh(user)
        return True, "Nama lengkap berhasil diubah."

def login_with_google():
    flow = Flow.from_client_secrets_file(
        "client_secrets.json",
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    
    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
    
    st.markdown(f'<a href="{auth_url}" target="_self" style="display: inline-block; padding: 10px 20px; font-size: 16px; font-weight: bold; color: white; background-color: #4285F4; text-decoration: none; border-radius: 5px;">Login dengan Google</a>', unsafe_allow_html=True)

# ------------------------------------------------
# --- CLASS MANAGEMENT UTILITIES ---
# ------------------------------------------------

def generate_class_code():
    return str(uuid.uuid4().hex[:6]).upper()

def create_new_class(db, creator_id, nama_kelas, deskripsi):
    code = generate_class_code()
    while db.query(Kelas).filter(Kelas.kode_kelas == code).first():
        code = generate_class_code()
        
    new_class = Kelas(
        nama_kelas=nama_kelas,
        deskripsi=deskripsi,
        kode_kelas=code,
        id_pembuat=creator_id
    )
    db.add(new_class)
    db.commit()
    db.refresh(new_class)
    
    join_class(db, creator_id, code)
    
    return True, f"Kelas **{nama_kelas}** berhasil dibuat! Kode Kelas: **{code}**"

def join_class(db, user_id, class_code):
    kelas = db.query(Kelas).filter(Kelas.kode_kelas == class_code).first()
    if not kelas:
        return False, "Kode kelas tidak valid."
        
    is_member = db.query(AnggotaKelas).filter(
        AnggotaKelas.id_kelas == kelas.id_kelas,
        AnggotaKelas.id_pengguna == user_id
    ).first()
    
    if is_member:
        return False, f"Anda sudah menjadi anggota kelas {kelas.nama_kelas}."
    
    try:
        new_member = AnggotaKelas(
            id_kelas=kelas.id_kelas,
            id_pengguna=user_id
        )
        db.add(new_member)
        db.commit()
        return True, f"Berhasil bergabung dengan kelas **{kelas.nama_kelas}**!"
    except IntegrityError:
        db.rollback()
        return False, "Gagal bergabung. Silakan coba lagi."

# ------------------------------------------------
# --- Gemini Integration ---
# ------------------------------------------------

def process_prompt_with_gemini(prompt):
    try:
        today = datetime.now().date()
        today_str = today.strftime("%Y-%m-%d")

        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(
            f"""Anda adalah asisten pengingat cerdas. Tugas Anda adalah:
              1. Menganalisis teks pengguna.
              2. Mendeteksi judul, deskripsi, tanggal, waktu, dan jenis pengingat (contoh: 'tugas', 'rapat', 'seragam').
              3. Jika pengguna menyebutkan tanggal relatif (misalnya: 'besok', 'minggu depan', 'hari jumat'), gunakan tanggal hari ini sebagai referensi untuk menghitung tanggal yang benar.
              4. Tanggal hari ini adalah: {today_str}.
              5. Jika tanggal yang diberikan adalah deadline, tentukan tanggal pengingat H-1.
              6. Mengembalikan output dalam format JSON seperti ini:
              {{
                "judul": "Judul pengingat yang diperbaiki",
                "deskripsi": "Deskripsi lengkap dari prompt",
                "tanggal_deadline": "YYYY-MM-DD",
                "jam_deadline": "HH:MM"
              }}
              Jika informasi tidak lengkap, isi dengan null. Teks untuk dianalisis:
              {prompt}
              """,
            generation_config=genai.GenerationConfig(
                response_mime_type='application/json'
            )
        )
        return response.text
    except Exception as e:
        st.error(f"Terjadi kesalahan saat menghubungi Gemini API: {e}")
        return None

# ------------------------------------------------
# --- UI BASE FUNCTIONS ---
# ------------------------------------------------

def login_ui():
    st.subheader("Masuk")
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Kata sandi", type="password", key="login_password")

    if st.button("Login", key="login_btn"):
        with SessionLocal() as db:
            user = get_user_by_email(db, email)
            if not user or (user.kata_sandi_hash and not bcrypt.verify(password, user.kata_sandi_hash)):
                st.error("Email atau kata sandi salah")
                return
            st.session_state["authentication_status"] = True
            st.session_state["user_info"] = {"name": user.nama_lengkap, "email": user.email, "user_id": user.id_pengguna}
            st.rerun()

    st.markdown("---")
    st.write("Atau masuk dengan:")
    login_with_google()

def register_ui():
    st.subheader("Daftar")
    with SessionLocal() as db:
        nama = st.text_input("Nama lengkap", key="register_nama")
        email = st.text_input("Email", key="register_email")
        password = st.text_input("Kata sandi", type="password", key="register_password")
        
        if st.button("Buat Akun", key="register_btn"):
            if get_user_by_email(db, email):
                st.error("Email sudah terdaftar")
            else:
                create_user(db, nama, email, password)
                st.success("Akun berhasil dibuat. Silakan login.")

# --- PERBAIKAN DI SINI ---
# Fungsi navbar disederhanakan, semua gaya dipindahkan ke CSS di main()
def navbar():
    with st.sidebar:
        selected = option_menu(
            menu_title=None,
            options=[
                "Chatbot", "Daftar Pengingat", "Jadwal Pelajaran",
                "Manajemen Kelas", "Riwayat Notifikasi", "Pengaturan Akun", "Logout"
            ],
            icons=[
                "chat-dots", "list-task", "book", "grid",
                "clock-history", "gear", "box-arrow-right"
            ],
            default_index=0,
        )

    if selected == "Logout":
        st.session_state.clear()
        st.rerun()

    return selected

# ------------------------------------------------
# --- UI PAGES ---
# ------------------------------------------------

def page_jadwal_pelajaran():
    user_id = st.session_state["user_info"]["user_id"]
    st.header("📚 Jadwal Pelajaran")

    hari_options = [h.value for h in Hari]

    with st.expander("➕ Tambah Jadwal Baru"):
        with st.form("form_tambah_jadwal", clear_on_submit=True):
            display_hari_options = [h.capitalize() for h in hari_options]
            hari_display = st.selectbox("Hari", display_hari_options, key="jadwal_hari_display")
            hari_input = hari_display.lower()
            pelajaran_input = st.text_input("Nama Mata Pelajaran", key="jadwal_pelajaran")
            col1, col2 = st.columns(2)
            with col1:
                jam_mulai_input = st.time_input("Jam Mulai", value=time(8, 0), key="jadwal_mulai")
            with col2:
                jam_selesai_input = st.time_input("Jam Selesai", value=time(9, 0), key="jadwal_selesai")
            
            submitted = st.form_submit_button("Simpan Jadwal")

            if submitted:
                if pelajaran_input:
                    with SessionLocal() as db:
                        new_jadwal = JadwalPelajaran(
                            id_pengguna=user_id,
                            hari=Hari(hari_input),
                            nama_pelajaran=pelajaran_input,
                            jam_mulai=jam_mulai_input,
                            jam_selesai=jam_selesai_input
                        )
                        db.add(new_jadwal)
                        db.commit()
                        st.success(f"Jadwal {pelajaran_input} untuk hari {hari_display} berhasil ditambahkan!")
                        st.rerun()
                else:
                    st.error("Nama Mata Pelajaran tidak boleh kosong.")

    st.subheader("Jadwal Anda")
    with SessionLocal() as db:
        jadwal_list = (
            db.query(JadwalPelajaran)
            .filter(JadwalPelajaran.id_pengguna == user_id)
            .order_by(JadwalPelajaran.hari, JadwalPelajaran.jam_mulai)
            .all()
        )
        
        jadwal_by_day = {h.value: [] for h in Hari}
        for j in jadwal_list:
            jadwal_by_day[j.hari.value].append(j)

        for hari_val in hari_options:
            if jadwal_by_day[hari_val]:
                with st.expander(f"**{hari_val.capitalize()}** ({len(jadwal_by_day[hari_val])} Pelajaran)"):
                    for j in jadwal_by_day[hari_val]:
                        colA, colB, colC = st.columns([0.2, 0.6, 0.2])
                        colA.write(f"**{j.jam_mulai.strftime('%H:%M')} - {j.jam_selesai.strftime('%H:%M')}**")
                        colB.write(f"{j.nama_pelajaran}")
                        
                        if colC.button("Hapus", key=f"del_{j.id_jadwal}"):
                            db.delete(j)
                            db.commit()
                            st.warning("Jadwal dihapus. Memuat ulang...")
                            st.rerun()

def page_kelas_management():
    user_id = st.session_state["user_info"]["user_id"]
    st.header("🏢 Manajemen Kelas")
    
    tab1, tab2 = st.tabs(["Buat Kelas Baru", "Bergabung Kelas"])

    with tab1:
        st.subheader("Buat Kelas")
        with st.form("form_buat_kelas", clear_on_submit=True):
            nama_kelas = st.text_input("Nama Kelas (Contoh: IPA Kelas X-A)")
            deskripsi = st.text_area("Deskripsi Kelas (Opsional)")
            submitted = st.form_submit_button("Buat Kelas")

            if submitted:
                if nama_kelas:
                    with SessionLocal() as db:
                        success, message = create_new_class(db, user_id, nama_kelas, deskripsi)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error("Gagal membuat kelas.")
                else:
                    st.error("Nama kelas tidak boleh kosong.")
                    
    with tab2:
        st.subheader("Bergabung dengan Kelas")
        with st.form("form_join_kelas", clear_on_submit=True):
            kode_kelas = st.text_input("Kode Kelas", placeholder="Masukkan 6 digit kode kelas")
            submitted = st.form_submit_button("Gabung Sekarang")

            if submitted:
                if kode_kelas:
                    with SessionLocal() as db:
                        success, message = join_class(db, user_id, kode_kelas.upper())
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                else:
                    st.error("Kode kelas tidak boleh kosong.")
                    
    st.markdown("---")
    
    st.subheader("Daftar Kelas Anda")
    
    with SessionLocal() as db:
        kelas_dibuat = db.query(Kelas).filter(Kelas.id_pembuat == user_id).all()
        
        if kelas_dibuat:
            st.markdown("#### Kelas yang Anda Buat (Admin)")
            for kelas in kelas_dibuat:
                with st.expander(f"**{kelas.nama_kelas}** ({kelas.kode_kelas})"):
                    st.write(f"Deskripsi: {kelas.deskripsi or 'Tidak ada deskripsi'}")
                    st.markdown("---")
                    
                    st.markdown("##### Anggota Kelas:")
                    
                    anggota_list = db.query(Pengguna, AnggotaKelas).join(AnggotaKelas, AnggotaKelas.id_pengguna == Pengguna.id_pengguna).filter(AnggotaKelas.id_kelas == kelas.id_kelas).all()
                    
                    for pengguna, anggota in anggota_list:
                        if pengguna.id_pengguna == user_id:
                            st.write(f"✅ **{pengguna.nama_lengkap}** ({pengguna.email}) - Anda (Pembuat)")
                            continue
                            
                        colX, colY = st.columns([0.7, 0.3])
                        colX.write(f"▪️ {pengguna.nama_lengkap} ({pengguna.email})")
                        
                        if colY.button("Keluarkan", key=f"kick_{anggota.id_anggota_kelas}"):
                            db.delete(anggota)
                            db.commit()
                            st.success(f"Anggota {pengguna.nama_lengkap} dikeluarkan.")
                            st.rerun()
                            
        kelas_diikuti_ids = db.query(AnggotaKelas.id_kelas).filter(
            AnggotaKelas.id_pengguna == user_id
        ).subquery()
        
        kelas_diikuti = db.query(Kelas).filter(
            Kelas.id_kelas.in_(kelas_diikuti_ids),
            Kelas.id_pembuat != user_id
        ).all()
        
        if kelas_diikuti:
            st.markdown("#### Kelas yang Anda Ikuti")
            for kelas in kelas_diikuti:
                with st.container(border=True):
                    st.write(f"**{kelas.nama_kelas}**")
                    st.write(f"Deskripsi: {kelas.deskripsi}")
                    
                    if st.button(f"Keluar dari Kelas", key=f"leave_{kelas.id_kelas}"):
                        anggota = db.query(AnggotaKelas).filter(
                            AnggotaKelas.id_kelas == kelas.id_kelas,
                            AnggotaKelas.id_pengguna == user_id
                        ).first()
                        if anggota:
                            db.delete(anggota)
                            db.commit()
                            st.success(f"Anda keluar dari kelas {kelas.nama_kelas}.")
                            st.rerun()

def get_user_classes(db, user_id):
    kelas_dibuat = db.query(Kelas).filter(Kelas.id_pembuat == user_id).all()
    
    kelas_diikuti_ids = db.query(AnggotaKelas.id_kelas).filter(
        AnggotaKelas.id_pengguna == user_id
    ).subquery()
    
    kelas_diikuti = db.query(Kelas).filter(
        Kelas.id_kelas.in_(kelas_diikuti_ids),
        Kelas.id_pembuat != user_id
    ).all()
    
    all_classes = {k.id_kelas: k.nama_kelas for k in kelas_dibuat + kelas_diikuti}
    
    return all_classes

def page_chatbot():
    user_id = st.session_state["user_info"]["user_id"]
    user_name = st.session_state["user_info"]["name"]

    st.markdown("### Apa ada tugas minggu ini? Ayo buat pengingat!")

    with SessionLocal() as db:
        user_classes = get_user_classes(db, user_id)
        class_options = {"Pribadi": None}
        for id_kelas, nama_kelas in user_classes.items():
            class_options[nama_kelas] = id_kelas

        selected_class_name = st.selectbox(
            "Tujuan Pengingat",
            list(class_options.keys())
        )
        selected_class_id = class_options[selected_class_name]

    prompt = st.text_input(
        "Ketikkan tugas Anda",
        placeholder="Ketik seperti: 'ingatkan saya minggu depan saya ada tugas matematika jam 10'"
    )

    if st.button("➤", key="send_prompt"):
        if prompt.strip():
            with st.spinner("Memproses..."):
                json_string = process_prompt_with_gemini(prompt)
            if json_string:
                try:
                    parsed = json.loads(json_string)
                    judul = parsed.get("judul")
                    if not judul or judul.lower() == 'null' or judul.strip() == "":
                        st.error(
                            f"Maaf **{user_name}**, saya tidak dapat mengidentifikasi judul pengingat."
                        )
                        return
                    tanggal_deadline_obj = None
                    if parsed.get("tanggal_deadline"):
                        tanggal_deadline_obj = date.fromisoformat(parsed["tanggal_deadline"])
                    jam_deadline_obj = time.fromisoformat(parsed["jam_deadline"]) if parsed.get("jam_deadline") else time(7, 0)
                    tanggal_pengingat_obj = tanggal_deadline_obj - timedelta(days=1) if tanggal_deadline_obj else None

                    with SessionLocal() as db:
                        pengingat = Pengingat(
                            id_pembuat=user_id,
                            id_kelas=selected_class_id,
                            judul=judul,
                            deskripsi=parsed.get("deskripsi"),
                            tanggal_deadline=tanggal_deadline_obj,
                            jam_deadline=jam_deadline_obj,
                            tipe=parsed.get("jenis", "pribadi")
                        )
                        db.add(pengingat)
                        db.commit()
                        db.refresh(pengingat)

                        penerima_ids = [user_id] if not selected_class_id else [
                            a[0] for a in db.query(AnggotaKelas.id_pengguna).filter(
                                AnggotaKelas.id_kelas == selected_class_id
                            ).all()
                        ]
                        for p_id in penerima_ids:
                            penerima = PenerimaPengingat(
                                id_pengingat=pengingat.id_pengingat,
                                id_pengguna=p_id
                            )
                            db.add(penerima)

                        log_desc = f"Chatbot: {pengingat.judul} ({selected_class_name})"
                        log = RiwayatAktivitas(
                            id_pengguna=user_id,
                            jenis_aktivitas="tambah_pengingat",
                            deskripsi=log_desc
                        )
                        db.add(log)
                        db.commit()

                        st.success(f"Pengingat dibuat: {pengingat.judul}")
                        st.info(f"Tujuan: **{selected_class_name}**. Deadline: {pengingat.tanggal_deadline} {jam_deadline_obj}")
                except Exception as e:
                    st.error(f"Gagal memproses respons: {e}")
                    st.text(f"Respons mentah dari AI: {json_string}")

def page_list():
    user_id = st.session_state["user_info"]["user_id"]
    st.header("🗂️ Daftar Pengingat")
    
    with SessionLocal() as db:
        items = db.query(
            Pengingat, 
            Kelas, 
            Pengguna.nama_lengkap.label('pembuat_nama')
        ).outerjoin(Kelas, Pengingat.id_kelas == Kelas.id_kelas).join(
            Pengguna, Pengingat.id_pembuat == Pengguna.id_pengguna
        ).filter(
            (Pengingat.id_pembuat == user_id) | 
            (PenerimaPengingat.id_pengguna == user_id) 
        ).join(PenerimaPengingat, PenerimaPengingat.id_pengingat == Pengingat.id_pengingat).distinct().order_by(Pengingat.dibuat_pada.desc()).all()


        for i, (pengingat, kelas, pembuat_nama) in enumerate(items):
            label = "Pribadi"
            if kelas:
                label = f"{kelas.nama_kelas} (Oleh: {pembuat_nama})"
            
            label_header = f"[{label}] {pengingat.judul} | {pengingat.tanggal_deadline} {pengingat.jam_deadline.strftime('%H:%M')}"
            
            unique_base_key = f"{pengingat.id_pengingat}_{i}"
            
            with st.expander(label_header):
                st.subheader("Edit Pengingat")
                
                new_title = st.text_input(f"Judul", pengingat.judul, key=f"title_{unique_base_key}")
                new_desc = st.text_area(f"Deskripsi", pengingat.deskripsi or "", key=f"desc_{unique_base_key}")
                
                col1_e, col2_e = st.columns(2)
                with col1_e:
                    new_date = st.date_input(
                        f"Tanggal deadline", 
                        pengingat.tanggal_deadline or date.today(), 
                        key=f"date_{unique_base_key}"
                    )
                with col2_e:
                    new_time = st.time_input(
                        f"Jam deadline",
                        pengingat.jam_deadline or time(8, 30),
                        key=f"time_{unique_base_key}"
                    )
                
                col_save, col_delete = st.columns([1, 1])
                
                with col_save:
                    if st.button(f"Simpan Perubahan", key=f"save_{unique_base_key}"):
                        pengingat.judul = new_title
                        pengingat.deskripsi = new_desc
                        pengingat.tanggal_deadline = new_date
                        pengingat.jam_deadline = new_time
                        db.commit()
                        st.success("Perubahan berhasil disimpan.")
                        st.rerun()
                
                with col_delete:
                    if st.button("Hapus Pengingat", key=f"delete_{unique_base_key}", type="primary"):
                        db.query(PenerimaPengingat).filter(PenerimaPengingat.id_pengingat == pengingat.id_pengingat).delete()
                        
                        db.delete(pengingat)
                        db.commit()
                        st.warning(f"Pengingat '{pengingat.judul}' berhasil dihapus. Memuat ulang...")
                        st.rerun()

def page_riwayat_notifikasi():
    user_id = st.session_state["user_info"]["user_id"]
    st.header("⏳ Riwayat Notifikasi")

    col_title, col_button = st.columns([0.8, 0.2])
    with col_button:
        if st.button("🧹 Hapus Riwayat", key="clear_notif_history", type="primary"):
            with SessionLocal() as db:
                db.query(Notifikasi).filter(Notifikasi.id_pengguna == user_id).delete(synchronize_session=False)
                db.commit()
                st.success("Riwayat notifikasi berhasil dibersihkan. Memuat ulang...")
                st.rerun()

    with SessionLocal() as db:
        data_query = db.query(
            Pengingat.judul.label("Judul Pengingat"),
            Notifikasi.waktu_kirim.label("Waktu Kirim"),
            Pengguna.email.label("Email Penerima"),
            Notifikasi.metode.label("Metode"),
            Notifikasi.status.label("Status")
        ).join(
            Pengingat, Notifikasi.id_pengingat == Pengingat.id_pengingat
        ).join(
            Pengguna, Notifikasi.id_pengguna == Pengguna.id_pengguna
        ).filter(
            Notifikasi.id_pengguna == user_id
        ).order_by(Notifikasi.waktu_kirim.desc()).all()

        if data_query:
            riwayat_data = [
                {
                    "Judul Pengingat": row[0],
                    "Waktu Kirim": row[1].strftime("%Y-%m-%d %H:%M:%S"),
                    "Email Penerima": row[2],
                    "Metode": row[3].value,
                    "Status": row[4].value
                }
                for row in data_query
            ]
            st.dataframe(riwayat_data, use_container_width=True)
        else:
            st.info("Belum ada riwayat notifikasi yang tersimpan untuk Anda.")

def page_settings():
    user_id = st.session_state["user_info"]["user_id"]
    st.header("⚙️ Pengaturan Akun")
    user_info = st.session_state.get("user_info", {})

    with st.container(border=True):
        st.subheader("Ubah Nama Lengkap")
        current_nama = user_info.get("name")
        new_nama = st.text_input("Nama Lengkap Baru", value=current_nama, key="new_nama")

        if st.button("Ubah Nama", key="change_name_btn"):
            if not new_nama or new_nama == current_nama:
                st.error("Nama lengkap tidak boleh kosong atau sama dengan nama sebelumnya.")
            else:
                success, message = update_nama(user_id, new_nama)
                if success:
                    st.success(message)
                    st.session_state["user_info"]["name"] = new_nama
                    st.rerun()
                else:
                    st.error(message)

    with st.container(border=True):
        st.subheader("Ubah Kata Sandi")
        old_password = st.text_input(
            "Kata Sandi Lama (kosongkan jika login awal dengan Google)",
            type="password",
            help="Kosongkan jika Anda login menggunakan Google.",
            key="old_password"
        )
        new_password = st.text_input("Kata Sandi Baru", type="password", key="new_password")
        new_password_confirm = st.text_input("Verifikasi Kata Sandi Baru", type="password", key="new_password_confirm")

        if st.button("Ubah Kata Sandi", key="change_password_btn"):
            if not new_password or new_password != new_password_confirm:
                st.error("Kata sandi baru tidak cocok atau kosong.")
            else:
                success, message = update_password(
                    st.session_state["user_info"]["user_id"],
                    old_password,
                    new_password
                )
                if success:
                    st.success(message)
                    st.session_state.clear()
                    st.session_state["reset_message"] = "Kata sandi berhasil diubah. Silakan login kembali."
                    st.rerun()
                else:
                    st.error(message)

# ------------------------------------------------
# --- MAIN APP ---
# ------------------------------------------------
def main():
    st.set_page_config(page_title="Chatbot Reminder", page_icon="⏰", layout="centered")

    # --- KODE DEBUGGING UNTUK MENEMUKAN CSS ---
    try:
        # Menggunakan pathlib untuk path yang lebih andal
        script_path = Path(__file__).resolve()
        script_dir = script_path.parent
        css_file_path = script_dir / "style.css"

        # Menampilkan pesan debug di aplikasi
        st.info(f"Mencari style.css di path: {css_file_path}")

        if css_file_path.is_file():
            st.success("File style.css berhasil ditemukan!")
            with open(css_file_path) as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        else:
            st.warning("PERINGATAN: File style.css tidak ditemukan di path tersebut.")

    except NameError:
        # Jika __file__ tidak terdefinisi (misalnya saat dijalankan di notebook interaktif)
        st.warning("Tidak bisa menentukan path skrip secara otomatis.")
    except Exception as e:
        st.error(f"Terjadi error saat mencoba memuat CSS: {e}")
    # ---------------------------------------------

    st.markdown('<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css">', unsafe_allow_html=True)
    st.title("⏰ Chatbot Reminder Tugas")

    if "reset_message" in st.session_state:
        st.success(st.session_state["reset_message"])
        del st.session_state["reset_message"]

    query_params = st.query_params
    if "code" in query_params:
        flow = Flow.from_client_secrets_file(
            "client_secrets.json",
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )
        try:
            flow.fetch_token(code=query_params["code"])
            credentials = flow.credentials
            
            with build("oauth2", "v2", credentials=credentials) as service:
                user_info = service.userinfo().get().execute()
            
            user_email = user_info.get("email")
            user_name = user_info.get("name")
            
            with SessionLocal() as db:
                user = get_user_by_email(db, user_email)
                if not user:
                    user = create_user(db, user_name, user_email)
                
                st.query_params.clear()
                
                st.session_state["authentication_status"] = True
                st.session_state["user_info"] = {"name": user_name, "email": user_email, "user_id": user.id_pengguna}
                st.rerun()

        except Exception as e:
            st.error(f"Terjadi kesalahan saat otentikasi: {e}")
            st.query_params.clear()
    
    if "authentication_status" not in st.session_state or st.session_state["authentication_status"] is None:
        tab1, tab2 = st.tabs(["Masuk", "Daftar"])
        with tab1:
            login_ui()
        with tab2:
            register_ui()
    else:
        choice = navbar()
        if choice == "Chatbot":
            page_chatbot()
        elif choice == "Daftar Pengingat":
            page_list()
        elif choice == "Jadwal Pelajaran":
            page_jadwal_pelajaran()
        elif choice == "Manajemen Kelas":
            page_kelas_management()
        elif choice == "Riwayat Notifikasi":
            page_riwayat_notifikasi()
        elif choice == "Pengaturan Akun":
            page_settings()

if __name__ == "__main__":
    if not os.path.exists("client_secrets.json"):
        st.error("File 'client_secrets.json' tidak ditemukan. Pastikan Anda telah mengunduhnya dari Google Cloud Console.")
    else:
        main()