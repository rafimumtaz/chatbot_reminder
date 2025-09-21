import streamlit as st
import streamlit_authenticator as stauth
from dotenv import load_dotenv
import os
import json
from datetime import date, time, timedelta, datetime

import google.generativeai as genai
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from passlib.hash import bcrypt

from database import SessionLocal
from models import Pengguna, Peran, Pengingat, PenerimaPengingat, RiwayatAktivitas

# Menggunakan Streamlit secrets untuk kredensial
CLIENT_ID = st.secrets["google"]["GOOGLE_CLIENT_ID"]
CLIENT_SECRET = st.secrets["google"]["GOOGLE_CLIENT_SECRET"]

# Inisialisasi Gemini API
genai.configure(api_key=st.secrets["gemini"]["GEMINI_API_KEY"])

# URL callback (redirect URI) harus cocok dengan yang di Google Cloud Console
REDIRECT_URI = "http://localhost:8501/"
SCOPES = ["openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"]

# --- AUTH UTILITIES ---
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

# --- Gemini Integration ---
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

# --- UI ---
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
        st.write(f"Selamat datang, **{st.session_state['user_info']['name']}**!")
        choice = st.radio("Menu", ["Chatbot", "Daftar Pengingat", "Pengaturan Akun"])
        if st.button("Keluar"):
            st.session_state.clear()
            st.rerun()
        return choice

# --- PAGES ---
def page_chatbot():
    user_id = st.session_state["user_info"]["user_id"]
    st.header("💬 Chatbot Reminder")
    st.write("Ketik seperti: **'ingatkan saya minggu depan saya ada tugas matematika jam 10'**")

    prompt = st.text_input("Pesan Anda")
    if st.button("Kirim") and prompt.strip():
        with st.spinner("Memproses..."):
            json_string = process_prompt_with_gemini(prompt)

        if json_string:
            try:
                parsed = json.loads(json_string)
                
                # Mendapatkan tanggal deadline dari respons AI
                tanggal_deadline_obj = None
                if parsed.get("tanggal_deadline"):
                    tanggal_deadline_obj = date.fromisoformat(parsed["tanggal_deadline"])
                    
                # Mengatur jam deadline atau default ke 07:00 jika 'null'
                jam_deadline_str = parsed.get("jam_deadline")
                jam_deadline_obj = None
                if jam_deadline_str and jam_deadline_str.lower() != 'null':
                    jam_deadline_obj = time.fromisoformat(jam_deadline_str)
                else:
                    jam_deadline_obj = time(7, 0)
                
                # Menghitung tanggal pengingat H-1
                tanggal_pengingat_obj = None
                if tanggal_deadline_obj:
                    tanggal_pengingat_obj = tanggal_deadline_obj - timedelta(days=1)

                with SessionLocal() as db:
                    pengingat = Pengingat(
                        id_pembuat=user_id,
                        judul=parsed.get("judul"),
                        deskripsi=parsed.get("deskripsi"),
                        tanggal_deadline=tanggal_deadline_obj,
                        jam_deadline=jam_deadline_obj,
                        tipe=parsed.get("jenis", "pribadi")
                    )
                    db.add(pengingat)
                    db.commit()
                    db.refresh(pengingat)

                    penerima = PenerimaPengingat(
                        id_pengingat=pengingat.id_pengingat,
                        id_pengguna=user_id
                    )
                    db.add(penerima)

                    log = RiwayatAktivitas(
                        id_pengguna=user_id,
                        jenis_aktivitas="tambah_pengingat",
                        deskripsi=f"Chatbot: {pengingat.judul}"
                    )
                    db.add(log)
                    db.commit()

                    st.success(f"Pengingat dibuat: {pengingat.judul}\nDeadline: {pengingat.tanggal_deadline} {jam_deadline_obj}")
                    st.info(f"Pengingat akan dikirim pada: {tanggal_pengingat_obj}")
            except Exception as e:
                st.error(f"Gagal memproses respons dari Gemini API: {e}")
                st.text(f"Respons mentah dari AI: {json_string}")

def page_list():
    user_id = st.session_state["user_info"]["user_id"]
    st.header("🗂️ Daftar Pengingat")
    with SessionLocal() as db:
        items = (
            db.query(Pengingat)
            .filter(Pengingat.id_pembuat == user_id)
            .order_by(Pengingat.dibuat_pada.desc())
            .all()
        )

        for it in items:
            with st.expander(f"{it.judul} | {it.tanggal_deadline} {it.jam_deadline}"):
                new_title = st.text_input(f"Judul #{it.id_pengingat}", it.judul, key=f"title_{it.id_pengingat}")
                new_desc = st.text_area(f"Deskripsi #{it.id_pengingat}", it.deskripsi or "", key=f"desc_{it.id_pengingat}")
                new_date = st.date_input(f"Tanggal deadline #{it.id_pengingat}", it.tanggal_deadline or date.today(), key=f"date_{it.id_pengingat}")
                new_time = st.time_input(
                    f"Jam deadline #{it.id_pengingat}",
                    it.jam_deadline or time(8, 30),
                    key=f"time_{it.id_pengingat}"
                )

                if st.button(f"Simpan #{it.id_pengingat}"):
                    it.judul = new_title
                    it.deskripsi = new_desc
                    it.tanggal_deadline = new_date
                    it.jam_deadline = new_time
                    db.commit()
                    st.success("Tersimpan.")

def page_settings():
    st.header("⚙️ Pengaturan Akun")
    st.info("Untuk demo lokal, Google Sign-In & verifikasi email belum diaktifkan.")
    user_info = st.session_state.get("user_info", {})
    user_id = user_info.get("user_id")

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

# --- MAIN ---
def main():
    st.set_page_config(page_title="Chatbot Reminder", page_icon="⏰", layout="centered")
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
                
                st.query_params.pop("code", None)
                
                st.session_state["authentication_status"] = True
                st.session_state["user_info"] = {"name": user_name, "email": user_email, "user_id": user.id_pengguna}
                st.rerun()

        except Exception as e:
            st.error(f"Terjadi kesalahan saat otentikasi: {e}")
            st.query_params.pop("code", None)
    
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
        elif choice == "Pengaturan Akun":
            page_settings()

if __name__ == "__main__":
    if not os.path.exists("client_secrets.json"):
        st.error("File 'client_secrets.json' tidak ditemukan. Pastikan Anda telah mengunduhnya dari Google Cloud Console.")
    else:
        main()