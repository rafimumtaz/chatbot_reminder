        
import streamlit as st
from sqlalchemy import func
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
def get_user_role_id(db, user_id):
    """Mengambil ID peran (role ID) pengguna."""
    user = db.query(Pengguna).filter(Pengguna.id_pengguna == user_id).first()
    return user.id_peran if user else None

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

def create_new_class(db, creator_id, nama_kelas, deskripsi, wali_kelas):
    # PERBAIKAN: Pemeriksaan Role ID 2 (Guru)
    user_role_id = get_user_role_id(db, creator_id)
    if user_role_id != 2:
         return False, "Akses Ditolak. Hanya pengguna dengan peran Guru (Role ID 2) yang dapat membuat kelas."

    code = generate_class_code()
    while db.query(Kelas).filter(Kelas.kode_kelas == code).first():
        code = generate_class_code()
        
    new_class = Kelas(
        nama_kelas=nama_kelas,
        deskripsi=deskripsi,
        kode_kelas=code,
        id_pembuat=creator_id,
        wali_kelas=wali_kelas
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
        
    existing_membership = db.query(AnggotaKelas).filter(
        AnggotaKelas.id_pengguna == user_id
    ).first()
    
    if existing_membership:
        if existing_membership.id_kelas == kelas.id_kelas:
            return False, f"Anda sudah menjadi anggota di kelas **{kelas.nama_kelas}**."
    
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

def get_user_classes(db, user_id):
    """Mengambil daftar kelas yang dibuat atau diikuti pengguna."""
    kelas_dibuat = db.query(Kelas).filter(Kelas.id_pembuat == user_id).all()
    kelas_diikuti_ids = db.query(AnggotaKelas.id_kelas).filter(AnggotaKelas.id_pengguna == user_id).subquery()
    
    kelas_diikuti = db.query(Kelas).filter(
        Kelas.id_kelas.in_(kelas_diikuti_ids),
        Kelas.id_pembuat != user_id
    ).all()
    
    all_classes = {k.id_kelas: k.nama_kelas for k in kelas_dibuat + kelas_diikuti}
    
    return all_classes
# ------------------------------------------------
# --- Gemini Integration ---
# ------------------------------------------------

def process_prompt_with_gemini(prompt):
    try:
        today = datetime.now().date()
        today_str = today.strftime("%Y-%m-%d")

        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(
            f"""Anda adalah asisten pengingat cerdas. Tugas Anda adalah:
             1. Menganalisis teks pengguna.
             2. Mendeteksi judul, deskripsi, tanggal, waktu.
             3. **DETEKSI KELAS/TUJUAN**: Cari nama kelas yang spesifik, biasanya memiliki pola seperti 'kelas X-Y' atau 'kelas [Nama Tertentu]'. Jika Anda mendeteksi nama kelas atau grup (misal: 'kelas 12-9'), gunakan nama tersebut secara eksak sebagai nilai untuk kunci 'jenis'. Jika tidak ada nama kelas yang spesifik, gunakan nilai 'pribadi'.
             4. Jika pengguna menyebutkan tanggal relatif (misalnya: 'besok', 'minggu depan', 'hari jumat'), gunakan tanggal hari ini sebagai referensi: {today_str}.
             5. Jika tanggal yang diberikan adalah deadline, tentukan tanggal pengingat H-1.
             6. Mengembalikan output dalam format JSON seperti ini:
             {{
                "judul": "Judul pengingat yang diperbaiki",
                "deskripsi": "Deskripsi lengkap dari prompt",
                "tanggal_deadline": "YYYY-MM-DD",
                "jam_deadline": "HH:MM",
                "jenis": "nama_kelas_atau_pribadi"
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

def navbar():
    with st.sidebar:
        selected = option_menu(
            menu_title=None,
            options=[
                "Chatbot", "Daftar Pengingat", "Jadwal Pelajaran",
                "Manajemen Kelas", "Riwayat", "Pengaturan Akun", "Logout"
            ],
            icons=[
                "chat-dots", "list-task", "book", "grid",
                "clock-history", "gear", "box-arrow-right"
            ],
            default_index=0,
            styles={
                "container": {
                    "padding": "0px !important",
                    "background-color": "transparent",
                },
                "icon": {
                    "color": "white",
                    "font-size": "1.2rem"
                },
                "nav-link": {
                    "font-size": "1rem",
                    "text-align": "left",
                    "margin": "0px 0px 10px 0px",
                    "padding": "0.75rem 1rem",
                    "color": "#FFFFFF",
                    "background-color": "#616161",
                    "border-radius": "10px",
                    "--hover-color": "#757575", 
                },
                "nav-link-selected": {
                    "background-color": "#424242", 
                },
            }
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

    st.markdown("""
    <style>
        /* Mengatur header utama halaman */
        .schedule-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
        }
        .schedule-header h1 {
            margin: 0;
            font-size: 2.5rem;
            color: #31333F;
        }
        .schedule-header .stButton>button {
            border-radius: 50%;
            width: 50px;
            height: 50px;
            font-size: 24px;
            background-color: #F0F2F6;
            color: #31333F;
            border: 1px solid #D7D9DC;
        }

        .schedule-row {
            display: flex;
            flex-wrap: nowrap;
            overflow-x: auto;
            padding-bottom: 20px;
            margin-bottom: 2rem;
        }

        .schedule-card {
            flex: 0 0 280px; 
            margin-right: 20px;
            border-radius: 12px; 
            border: 1px solid #E0E0E0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            overflow: hidden; 
            display: flex;
            flex-direction: column;
        }

        .card-top {
            background-color: #616161;
            color: white;
            padding: 15px;
        }
        .card-top h4 { font-size: 1.1rem; margin: 0 0 5px 0; padding: 0; }
        .card-top p { font-size: 0.9rem; margin: 0; padding: 0; }

        .card-bottom {
            background-color: #F5F5F5;
            padding: 10px 15px;
            flex-grow: 1;
            display: flex;
            align-items: center;
            justify-content: flex-end; 
        }
        
        .schedule-card .stButton>button {
            background-color: #FF4B4B !important; 
            color: white !important;             
            border-radius: 8px !important;
            border: none !important;
            padding: 5px 15px !important;
        }
        .schedule-card .stButton>button:hover {
            background-color: #E03C3C !important;
            color: white !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # --- Header Halaman ---
    if 'show_jadwal_form' not in st.session_state:
        st.session_state.show_jadwal_form = False
    
    header_cols = st.columns([0.85, 0.15])
    with header_cols[0]:
        st.markdown("<div class='schedule-header'><h1>Jadwal Pelajaran</h1></div>", unsafe_allow_html=True)
    with header_cols[1]:
        if st.button("＋", key="add_schedule"):
            st.session_state.show_jadwal_form = not st.session_state.show_jadwal_form

    # --- Form Tambah Jadwal ---
    if st.session_state.show_jadwal_form:
        with st.expander("➕ Tambah Jadwal Baru", expanded=True):
            with st.form("form_tambah_jadwal", clear_on_submit=True):
                hari_options = [h.value for h in Hari]
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
                                id_pengguna=user_id, hari=Hari(hari_input),
                                nama_pelajaran=pelajaran_input,
                                jam_mulai=jam_mulai_input, jam_selesai=jam_selesai_input
                            )
                            db.add(new_jadwal)
                            db.commit()
                            st.success(f"Jadwal {pelajaran_input} berhasil ditambahkan!")
                            st.rerun()
                    else:
                        st.error("Nama Mata Pelajaran tidak boleh kosong.")
    
    with SessionLocal() as db:
        jadwal_list = db.query(JadwalPelajaran).filter(JadwalPelajaran.id_pengguna == user_id).order_by(JadwalPelajaran.hari, JadwalPelajaran.jam_mulai).all()
        jadwal_by_day = {h.value: [] for h in Hari}
        for j in jadwal_list:
            jadwal_by_day[j.hari.value].append(j)

        for hari_val, jadwal_harian in jadwal_by_day.items():
            if jadwal_harian:
                st.subheader(hari_val.capitalize())
                
                st.markdown('<div class="schedule-row">', unsafe_allow_html=True)
                for j in jadwal_harian:
                    card_html = f"""
                        <div class="schedule-card">
                            <div class="card-top">
                                <h4>{j.nama_pelajaran}</h4>
                                <p>{j.jam_mulai.strftime('%H:%M')} - {j.jam_selesai.strftime('%H:%M')}</p>
                            </div>
                            <div class="card-bottom">
                                </div>
                        </div>
                    """
                    with st.container():
                        st.markdown(card_html, unsafe_allow_html=True)
                        if st.button("Hapus", key=f"del_{j.id_jadwal}"):
                             with SessionLocal() as db_inner:
                                jadwal_to_delete = db_inner.query(JadwalPelajaran).filter(JadwalPelajaran.id_jadwal == j.id_jadwal).first()
                                if jadwal_to_delete:
                                    db_inner.delete(jadwal_to_delete)
                                    db_inner.commit()
                                    st.rerun()

                st.markdown('</div>', unsafe_allow_html=True)

def page_kelas_management():
    user_id = st.session_state["user_info"]["user_id"]
    user_role_id = st.session_state.get("user_role_id")
    is_guru = user_role_id == 2
    
    st.header("🏢 Manajemen Kelas")
    
    # ----------------------------------------------------
    # --- BAGIAN 1: Fungsionalitas Guru (Membuat & Mengelola) ---
    # ----------------------------------------------------
    if is_guru:
        st.markdown("### 👩‍🏫 Akses Guru: Buat dan Kelola")
        tab1, tab2 = st.tabs(["Buat Kelas Baru", "Kelola Anggota"])

        # TAB 1: Buat Kelas Baru (TERMASUK DAFTAR KELAS AKTIF GURU)
        with tab1:
            st.subheader("Buat Kelas")
            with st.form("form_buat_kelas", clear_on_submit=True):
                nama_kelas = st.text_input("Nama Kelas (Contoh: IPA Kelas X-A)")
                wali_kelas = st.text_input("Nama Wali Kelas", placeholder="Masukkan nama wali kelas")
                deskripsi = st.text_area("Deskripsi Kelas (Opsional)")
                submitted = st.form_submit_button("Buat Kelas")

                if submitted:
                    if nama_kelas and wali_kelas:
                        with SessionLocal() as db:
                            success, message = create_new_class(db, user_id, nama_kelas, deskripsi, wali_kelas) 
                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)
                    else:
                        st.error("Nama kelas dan Nama Wali Kelas tidak boleh kosong.")
                        
            st.markdown("---")
            # --- DAFTAR KELAS AKTIF GURU (BARU) ---
            st.markdown("##### Kelas Aktif:")
            with SessionLocal() as db:
                kelas_dibuat = db.query(Kelas).filter(Kelas.id_pembuat == user_id).all()
                if kelas_dibuat:
                    for kelas in kelas_dibuat:
                         with st.container(border=True):
                            st.write(f"**{kelas.nama_kelas}** (Kode: `{kelas.kode_kelas}`)")
                            st.write(f"Wali Kelas: {kelas.wali_kelas or 'Tidak Ada'}")
                else:
                    st.info("Anda belum membuat kelas.")
            # --- END DAFTAR KELAS AKTIF GURU ---
                        
        # TAB 2: Kelola Anggota (Hanya Guru)
        with tab2:
            st.subheader("Kelola Anggota Kelas Anda")
            st.info("Anda hanya dapat mengeluarkan anggota dari kelas yang Anda buat.")
            
            with SessionLocal() as db:
                kelas_dibuat = db.query(Kelas).filter(Kelas.id_pembuat == user_id).all()
                
                if kelas_dibuat:
                    for kelas in kelas_dibuat:
                        with st.expander(f"**{kelas.nama_kelas}** ({kelas.kode_kelas})"):
                            st.write(f"Wali Kelas: **{kelas.wali_kelas or 'Tidak Ada'}**")
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
                else:
                    st.info("Anda belum membuat kelas.")

        st.markdown("---")
    
    # ----------------------------------------------------
    # --- BAGIAN 2: Fungsionalitas Siswa (Bergabung & Lihat) ---
    # ----------------------------------------------------
    
    # Form Bergabung Kelas - HANYA DITAMPILKAN JIKA BUKAN GURU
    if not is_guru: 
        st.markdown("### 🧑‍🎓 Kelas Anda")
        with st.container(border=True):
            st.subheader("Bergabung dengan Kelas Baru")
            st.info("Anda hanya dapat bergabung dengan satu kelas aktif.")
            
            with st.form("form_join_kelas_universal", clear_on_submit=True):
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

        # Daftar Kelas yang Diikuti (Untuk semua pengguna)
        with SessionLocal() as db:
            kelas_diikuti_ids = db.query(AnggotaKelas.id_kelas).filter(AnggotaKelas.id_pengguna == user_id).subquery()
            
            all_class_memberships = db.query(Kelas).filter(
                Kelas.id_kelas.in_(kelas_diikuti_ids)
            ).all()
            
            if all_class_memberships:
                st.markdown("#### Kelas Aktif:")
                for kelas in all_class_memberships:
                    is_creator = kelas.id_pembuat == user_id
                    
                    with st.container(border=True):
                        status = "Dibuat Anda" if is_creator else "Anggota"
                        st.write(f"**{kelas.nama_kelas}** ({status})")
                        st.write(f"Wali Kelas: {kelas.wali_kelas or 'Tidak Ada'}")
                        st.write(f"Kode: `{kelas.kode_kelas}`")
                        
                        if not is_creator:
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
            else:
                st.info("Anda belum bergabung atau membuat kelas apa pun.")

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

    st.markdown("""
    <style>
        section.main > div {
            display: flex; 
            flex-direction: column; 
            justify-content: center; 
            align-items: center; 
            min-height: 85vh; 
        }
        
        p.chat-header {
            background-color: #E0E0E0;
            padding: 8px 16px;
            border-radius: 15px;
            font-weight: bold;
            color: #4F4F4F;
            display: inline-block;
            margin-bottom: 2rem; 
        }

        h3.chat-title {
            text-align: center;
            font-weight: 500;
            color: #4f4f4f;
            padding: 0;
            margin: 0 0 1.5rem 0;
        }

        div[data-testid="stForm"] {
            margin: 0 auto;
            max-width: 700px;
            width: 100%;
        }

        div[data-testid="stForm"] form {
            display: flex;
            align-items: center;
            background-color: #4F4F4F;
            border-radius: 30px;
            padding-left: 25px;
            padding-right: 10px;
            height: 60px;
        }

        div[data-testid="stTextInput"] {
            flex-grow: 1;
        }

        div[data-testid="stTextInput"] input {
            background-color: transparent;
            color: black;
            border: none;
            padding: 0;
            margin: 0;
            height: 100%;
            font-size: 1rem;
        }
        
        div[data-testid="stTextInput"] input::placeholder {
            color: #BDBDBD;
        }

        div[data-testid="stTextInput"] input:focus {
            box-shadow: none;
        }

        div[data-testid="stFormSubmitButton"] {
            flex-grow: 0;
        }

        div[data-testid="stFormSubmitButton"] button {
            background: transparent;
            border: none;
            color: white;
            font-size: 28px;
            cursor: pointer;
            padding: 0 15px;
        }
        
        div[data-testid="stFormSubmitButton"] button:hover,
        div[data-testid="stFormSubmitButton"] button:focus {
            color: #BDBDBD;
            border: none;
            box-shadow: none !important;
            background-color: transparent !important;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<p class='chat-header'>ChatMyre</p>", unsafe_allow_html=True)
    st.markdown("<h3 class='chat-title'>Apa ada tugas minggu ini? Ayo buat pengingat!</h3>", unsafe_allow_html=True)

    

    with st.form(key="chat_form"):
        prompt = st.text_input(
            "Ketikkan tugas Anda",
            placeholder="Ketikkan tugas Anda",
            label_visibility="collapsed"
        )
        submitted = st.form_submit_button("➤")

        if submitted:
            if prompt.strip():
                selected_class_id = None
                selected_class_name = "Pribadi"
                
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
                        
                        detected_target_name = parsed.get("jenis", "pribadi")

                        if detected_target_name.lower() != 'pribadi':
                            standardized_name = detected_target_name.strip()
                            
                            with SessionLocal() as db_class_check:
                                search_names = [standardized_name]
                                
                                if standardized_name.lower().startswith("kelas "):
                                    search_names.append(standardized_name[6:].strip()) 
                                
                                found_class = None
                                
                                for name_to_search in search_names:
                                    found_class = db_class_check.query(Kelas).filter(
                                        Kelas.nama_kelas.ilike(name_to_search)
                                    ).first()

                                    if not found_class:
                                        found_class = db_class_check.query(Kelas).filter(
                                            func.lower(Kelas.nama_kelas) == name_to_search.lower() 
                                        ).first()

                                    if found_class:
                                        break
                                
                                if found_class:
                                    selected_class_id = found_class.id_kelas
                                    selected_class_name = found_class.nama_kelas
                                else:
                                    st.warning(f"AI mendeteksi tujuan: **{detected_target_name}**, tetapi kelas ini tidak ditemukan. Tujuan disetel sebagai **Pribadi**.")

                        tanggal_deadline_obj = None
                        if parsed.get("tanggal_deadline"):
                            tanggal_deadline_obj = date.fromisoformat(parsed["tanggal_deadline"])
                            
                        jam_deadline_str = parsed.get("jam_deadline")
                        jam_deadline_obj = time.fromisoformat(jam_deadline_str) if jam_deadline_str and jam_deadline_str.lower() != 'null' else time(7, 0)

                        tanggal_pengingat_obj = tanggal_deadline_obj - timedelta(days=1) if tanggal_deadline_obj else None

                        with SessionLocal() as db:
                            if selected_class_id and tanggal_deadline_obj:
                                existing_reminder = db.query(Pengingat).filter(
                                    Pengingat.id_kelas == selected_class_id,
                                    Pengingat.judul == judul,
                                    Pengingat.tanggal_deadline == tanggal_deadline_obj
                                ).first()

                                if existing_reminder:
                                    st.warning(
                                        f"🔔 Pengingat dengan judul **'{judul}'** untuk kelas **{selected_class_name}** pada tanggal **{tanggal_deadline_obj.strftime('%d-%m-%Y')}** sudah ada. Pembuatan pengingat dibatalkan."
                                    )
                                    return 
                            pengingat = Pengingat(
                                id_pembuat=user_id,
                                id_kelas=selected_class_id, 
                                judul=judul,
                                deskripsi=parsed.get("deskripsi"),
                                tanggal_deadline=tanggal_deadline_obj,
                                jam_deadline=jam_deadline_obj,
                                tipe=selected_class_name 
                            )
                            db.add(pengingat)
                            db.commit()
                            db.refresh(pengingat)

                            if selected_class_id:
                                anggota = db.query(AnggotaKelas.id_pengguna).filter(AnggotaKelas.id_kelas == selected_class_id).all()
                                penerima_ids = [a[0] for a in anggota]
                            else:
                                penerima_ids = [user_id] 
                            
                            for p_id in penerima_ids:
                                penerima = PenerimaPengingat(id_pengingat=pengingat.id_pengingat, id_pengguna=p_id)
                                db.add(penerima)
                            
                            log_desc = f"Chatbot: {pengingat.judul} (Tujuan: {selected_class_name})"
                            log = RiwayatAktivitas(id_pengguna=user_id, jenis_aktivitas="tambah pengingat", deskripsi=log_desc)
                            db.add(log); 
                            db.commit()
                            
                            st.success(f"Pengingat dibuat: {pengingat.judul}")
                            st.info(f"Tujuan: **{selected_class_name}**. Deadline: {pengingat.tanggal_deadline} {jam_deadline_obj}") 
                    
                    except Exception as e:
                        st.error(f"Gagal memproses respons: Terjadi kesalahan teknis. ({e})")
                        st.text(f"Respons mentah dari AI: {json_string}")

                       

def page_list():
    user_id = st.session_state["user_info"]["user_id"]

    # --- CSS Khusus untuk Halaman Daftar Pengingat ---
    st.markdown("""
    <style>
        /* Header utama halaman */
        .reminder-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
            border-bottom: 2px solid #E0E0E0;
            padding-bottom: 1rem;
        }
        /* Tombol Tambah (+) */
        .reminder-header .stButton>button {
            border-radius: 10px;
            width: 50px;
            height: 50px;
            font-size: 32px;
            font-weight: 300;
            background-color: #F0F2F6;
            color: #31333F;
            border: 1px solid #D7D9DC;
        }

        /* Tampilan Tanggal Realtime */
        .date-display {
            text-align: right;
        }
        .date-display .date-text {
            font-size: 1.5rem;
            font-weight: bold;
            color: #31333F;
            margin: 0;
        }
        .date-display .day-text {
            font-size: 1.1rem;
            color: #616161;
            margin: 0;
        }
        
        /* Mengatur setiap item pengingat (st.expander) */
        div[data-testid="stExpander"] {
            border: none !important;
            box-shadow: none !important;
            margin-bottom: 10px;
        }
        div[data-testid="stExpander"] > details {
            border-radius: 10px;
            background-color: #E0E0E0; /* Warna abu-abu terang */
        }
        div[data-testid="stExpander"] > details > summary {
            font-size: 1rem;
            color: #31333F;
            padding: 15px;
        }
        /* Menghilangkan panah default dari expander */
        div[data-testid="stExpander"] > details > summary::marker,
        div[data-testid="stExpander"] > details > summary::-webkit-details-marker {
            display: none;
        }
        
        /* Gaya untuk form edit di dalam expander */
        .st-emotion-cache-1r6slb0 { /* Target container dalam expander */
            border-top: 1px solid #BDBDBD;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # --- State Management untuk Form Tambah ---
    if 'show_add_reminder_form' not in st.session_state:
        st.session_state.show_add_reminder_form = False

    # --- Header Halaman (Tombol +, Tanggal Realtime) ---
    header_cols = st.columns([0.15, 0.85])
    with header_cols[0]:
        if st.button("＋", key="add_new_reminder_plus"):
            st.session_state.show_add_reminder_form = not st.session_state.show_add_reminder_form
    with header_cols[1]:
        # Logika untuk mendapatkan tanggal dan hari realtime dalam Bahasa Indonesia
        now = datetime.now()
        day_map = {"Monday": "Senin", "Tuesday": "Selasa", "Wednesday": "Rabu", "Thursday": "Kamis", "Friday": "Jum'at", "Saturday": "Sabtu", "Sunday": "Minggu"}
        month_map = {1: "Januari", 2: "Februari", 3: "Maret", 4: "April", 5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus", 9: "September", 10: "Oktober", 11: "November", 12: "Desember"}
        
        date_str = f"{now.day} {month_map[now.month]}, {now.year}"
        day_str = day_map[now.strftime("%A")]
        
        st.markdown(f"""
            <div class="date-display">
                <p class="date-text">{date_str}</p>
                <p class="day-text">{day_str}</p>
            </div>
        """, unsafe_allow_html=True)
        
    # --- Form Tambah Pengingat Manual (muncul saat + diklik) ---
    if st.session_state.show_add_reminder_form:
        with st.expander("Buat Pengingat Baru", expanded=True):
            # SEMUA LOGIKA FORM ANDA YANG LAMA DITEMPATKAN DI SINI
            with st.form("new_reminder_form", clear_on_submit=True):
                with SessionLocal() as db_class_check:
                    user_classes = get_user_classes(db_class_check, user_id)
                class_options = {"Pribadi": None, **{nama: id_ for id_, nama in user_classes.items()}}
                
                selected_class_name = st.selectbox("Tujuan Pengingat", list(class_options.keys()), key="add_rem_target")
                selected_class_id = class_options[selected_class_name]
                
                new_title = st.text_input("Judul Pengingat", key="add_rem_title")
                new_desc = st.text_area("Deskripsi", key="add_rem_desc")
                
                col1_add, col2_add = st.columns(2)
                with col1_add:
                    new_date = st.date_input("Tanggal Deadline", date.today(), key="add_rem_date")
                with col2_add:
                    new_time = st.time_input("Jam Deadline", time(8, 30), key="add_rem_time")
                
                if st.form_submit_button("Simpan Pengingat"):
                    if new_title:
                        with SessionLocal() as db:
                            pengingat = Pengingat(
                                id_pembuat=user_id, id_kelas=selected_class_id, judul=new_title,
                                deskripsi=new_desc, tanggal_deadline=new_date, jam_deadline=new_time,
                                tipe=selected_class_name
                            )
                            db.add(pengingat)
                            db.commit(); db.refresh(pengingat)
                            
                            penerima_ids = [user_id]
                            if selected_class_id:
                                anggota = db.query(AnggotaKelas.id_pengguna).filter(AnggotaKelas.id_kelas == selected_class_id).all()
                                penerima_ids = [a[0] for a in anggota]
                            
                            for p_id in penerima_ids:
                                db.add(PenerimaPengingat(id_pengingat=pengingat.id_pengingat, id_pengguna=p_id))
                            
                            db.commit()
                            st.success(f"Pengingat '{new_title}' berhasil ditambahkan.")
                            st.session_state.show_add_reminder_form = False
                            st.rerun()
                    else:
                        st.error("Judul pengingat tidak boleh kosong.")

    # --- Daftar Pengingat ---
    with SessionLocal() as db:
        items = db.query(Pengingat, Kelas, Pengguna.nama_lengkap.label('pembuat_nama')
            ).outerjoin(Kelas, Pengingat.id_kelas == Kelas.id_kelas
            ).join(Pengguna, Pengingat.id_pembuat == Pengguna.id_pengguna
            ).join(PenerimaPengingat, PenerimaPengingat.id_pengingat == Pengingat.id_pengingat
            ).filter(PenerimaPengingat.id_pengguna == user_id
            ).distinct().order_by(Pengingat.tanggal_deadline.asc(), Pengingat.jam_deadline.asc()
            ).all()

    st.markdown("---")
    
    # Menampilkan pengingat yang ada
    if not items:
        st.info("Belum ada pengingat untuk hari ini.")
    else:
        for i, (pengingat, kelas, pembuat_nama) in enumerate(items):
            # Membuat label untuk expander
            label_header = f"{pengingat.judul}"
            
            with st.expander(label_header):
                # SEMUA LOGIKA EDIT FORM ANDA YANG LAMA DITEMPATKAN DI SINI
                st.subheader("Edit Pengingat")
                unique_base_key = f"{pengingat.id_pengingat}_{i}"
                
                new_title = st.text_input("Judul", pengingat.judul, key=f"title_{unique_base_key}")
                new_desc = st.text_area("Deskripsi", pengingat.deskripsi or "", key=f"desc_{unique_base_key}")
                
                col1_e, col2_e = st.columns(2)
                with col1_e:
                    new_date = st.date_input("Tanggal deadline", pengingat.tanggal_deadline or date.today(), key=f"date_{unique_base_key}")
                with col2_e:
                    new_time = st.time_input("Jam deadline", pengingat.jam_deadline or time(8, 30), key=f"time_{unique_base_key}")
                
                col_save, col_delete = st.columns(2)
                with col_save:
                    if st.button("Simpan Perubahan", key=f"save_{unique_base_key}"):
                        with SessionLocal() as db_update:
                            p_to_update = db_update.query(Pengingat).get(pengingat.id_pengingat)
                            p_to_update.judul = new_title
                            p_to_update.deskripsi = new_desc
                            p_to_update.tanggal_deadline = new_date
                            p_to_update.jam_deadline = new_time
                            db_update.commit()
                        st.success("Perubahan berhasil disimpan.")
                        st.rerun()
                with col_delete:
                    if st.button("Hapus Pengingat", key=f"delete_{unique_base_key}", type="primary"):
                        with SessionLocal() as db_delete:
                            p_to_delete = db_delete.query(Pengingat).get(pengingat.id_pengingat)
                            db_delete.query(PenerimaPengingat).filter(PenerimaPengingat.id_pengingat == p_to_delete.id_pengingat).delete()
                            db_delete.delete(p_to_delete)
                            db_delete.commit()
                        st.warning(f"Pengingat '{pengingat.judul}' berhasil dihapus.")
                        st.rerun()

def page_riwayat_terpadu():
    # Pastikan user_info ada di session_state
    if "user_info" not in st.session_state:
        st.warning("Silakan login terlebih dahulu.")
        return

    user_id = st.session_state["user_info"]["user_id"]
    st.header("⏳ Riwayat Terpadu")
    st.caption("Menampilkan gabungan riwayat notifikasi dan aktivitas Anda.")

    # --- Tombol Hapus Riwayat ---
    if st.button("🧹 Hapus Semua Riwayat", key="clear_all_history", type="primary"):
        try:
            with SessionLocal() as db:
                db.query(Notifikasi).filter(Notifikasi.id_pengguna == user_id).delete(synchronize_session=False)
                db.query(RiwayatAktivitas).filter(RiwayatAktivitas.id_pengguna == user_id).delete(synchronize_session=False)
                db.commit()
                st.success("Semua riwayat berhasil dibersihkan. Memuat ulang...")
                st.rerun()
        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")

    st.divider()

    # --- Logika untuk Mengambil dan Menggabungkan Data ---
    combined_history = []
    with SessionLocal() as db:
        # 1. Ambil data Riwayat Notifikasi
        notifikasi_query = db.query(
            Pengingat.judul,
            Notifikasi.waktu_kirim,
            Notifikasi.status,
            Notifikasi.metode
        ).join(
            Pengingat, Notifikasi.id_pengingat == Pengingat.id_pengingat
        ).filter(
            Notifikasi.id_pengguna == user_id
        ).all()

        for row in notifikasi_query:
            combined_history.append({
                "tipe": "notifikasi",
                "timestamp": row.waktu_kirim,
                "judul": f"Pengingat: {row.judul}",
                "deskripsi": f"Status: **{row.status.value}** | Metode: **{row.metode.value}**"
            })

        # 2. Ambil data Riwayat Aktivitas
        aktivitas_query = db.query(
            RiwayatAktivitas.jenis_aktivitas,
            RiwayatAktivitas.deskripsi,
            RiwayatAktivitas.waktu
        ).filter(
            RiwayatAktivitas.id_pengguna == user_id
        ).all()

        for row in aktivitas_query:
            combined_history.append({
                "tipe": "aktivitas",
                "timestamp": row.waktu,
                "judul": row.jenis_aktivitas,
                "deskripsi": row.deskripsi
            })

    # --- Menampilkan Riwayat Gabungan ---
    if combined_history:
        # 3. Urutkan semua riwayat berdasarkan waktu (timestamp) dari yang terbaru
        # --- PERBAIKAN DI SINI ---
        # Mengganti None dengan tanggal minimum agar bisa diurutkan
        combined_history.sort(key=lambda item: item['timestamp'] if item['timestamp'] is not None else datetime.min, reverse=True)

        st.subheader("Aktivitas Terbaru Anda")

        # 4. Tampilkan dalam format feed (non-tabel)
        for item in combined_history:
            with st.container():
                # Jika timestamp tidak ada, tampilkan pesan khusus
                if item['timestamp'] is None:
                    timestamp_str = "Waktu tidak tercatat"
                else:
                    timestamp_str = item['timestamp'].strftime('%d %B %Y, %H:%M:%S')

                col_icon, col_info = st.columns([0.1, 0.9])
                
                with col_icon:
                    if item['tipe'] == 'notifikasi':
                        st.markdown("<h3 style='text-align: center;'>🔔</h3>", unsafe_allow_html=True)
                    else:
                        st.markdown("<h3 style='text-align: center;'>📝</h3>", unsafe_allow_html=True)

                with col_info:
                    st.markdown(f"**{item['judul']}**")
                    st.caption(timestamp_str)
                    st.write(item['deskripsi'])
                
                st.divider()
    else:
        st.info("Belum ada riwayat notifikasi atau aktivitas yang tersimpan untuk Anda.")
        
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
    st.markdown("""
    <style>
        /* Menata panel sidebar utama */
        [data-testid="stSidebar"] > div:first-child {
            background-color: #E0E0E0;
            padding: 1.5rem 1rem;
            display: flex;
            flex-direction: column;
            height: 100vh;
        }

        [data-testid="stSidebar"] ul {
            display: flex;
            flex-direction: column;
            flex-grow: 1;
            list-style: none;
            padding: 0;
            margin: 0;
        }

        [data-testid="stSidebar"] ul li:nth-last-child(2) {
            margin-top: auto;
        }

        div[data-testid="stExpander"] {
            border-radius: 12px !important;
            border: 1px solid #E0E0E0 !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
        }
        div[data-testid="stExpander"] > details > summary {
            font-size: 1.1rem !important;
        }

        .block-container {
            padding-top: 2rem !important;
        }

        /* Menyesuaikan tampilan st.expander secara global */
        div[data-testid="stExpander"] {
            border-radius: 12px !important;
            border: 1px solid #E0E0E0 !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
            margin-bottom: 1rem;
        }
        div[data-testid="stExpander"] > details > summary {
            font-size: 1.1rem !important;
        }   
    </style>
    """, unsafe_allow_html=True)
  
    if "reset_message" in st.session_state:
        st.success(st.session_state["reset_message"])
        del st.session_state["reset_message"]

    query_params = st.query_params
    
    # -----------------------------------------------------------------
    # --- BLOK 1: LOGIN GOOGLE (Menyimpan Role ID setelah berhasil) ---
    # -----------------------------------------------------------------
    if "code" in query_params:
        flow = Flow.from_client_secrets_file(
            "client_secrets.json", scopes=SCOPES, redirect_uri=REDIRECT_URI
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
                
                # --- PERBAIKAN: Menyimpan Role ID ---
                user_role_id = get_user_role_id(db, user.id_pengguna)
                st.session_state["user_role_id"] = user_role_id
                # ------------------------------------
                
                st.query_params.clear()
                st.session_state["authentication_status"] = True
                st.session_state["user_info"] = {"name": user_name, "email": user_email, "user_id": user.id_pengguna}
                st.rerun()
        except Exception as e:
            st.error(f"Terjadi kesalahan saat otentikasi: {e}")
            st.query_params.clear()
    
    # -----------------------------------------------------------------
    # --- BLOK 2: SETELAH LOGIN (Memeriksa dan Memuat Role ID) ---
    # -----------------------------------------------------------------
    if "authentication_status" not in st.session_state or st.session_state["authentication_status"] is None:
        tab1, tab2 = st.tabs(["Masuk", "Daftar"])
        with tab1:
            login_ui()
        with tab2:
            register_ui()
    else:
        # --- PERBAIKAN: Fallback Memuat Role ID Jika Hilang (Contoh: Setelah Rerun) ---
        if "user_role_id" not in st.session_state:
             with SessionLocal() as db:
                 user_id = st.session_state["user_info"]["user_id"]
                 st.session_state["user_role_id"] = get_user_role_id(db, user_id)
        # -------------------------------------------------------------------------
                 
        choice = navbar()
        
        # Logika routing
        if choice == "Chatbot":
            page_chatbot()
        elif choice == "Daftar Pengingat":
            page_list()
        elif choice == "Jadwal Pelajaran":
            page_jadwal_pelajaran()
        elif choice == "Manajemen Kelas":
            page_kelas_management()
        elif choice == "Riwayat":
            page_riwayat_terpadu()
        elif choice == "Pengaturan Akun":
            page_settings()

if __name__ == "__main__":
    if not os.path.exists("client_secrets.json"):
        st.error("File 'client_secrets.json' tidak ditemukan. Pastikan Anda telah mengunduhnya dari Google Cloud Console.")
    else:
        main()