import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import requests

# --- 1. KONFIGURASI API ---
# Masukkan API Key ImgBB Anda di sini
API_IMGBB = "45ef23a8d4da7b8ed4acfea2a00c76a7"

st.set_page_config(page_title="Absensi Tim KI", layout="centered")

# --- 2. LOGIKA SAPAAN & WAKTU (WIB) ---
# Ambil waktu server lalu tambah 7 jam untuk Jakarta
waktu_wib = datetime.datetime.now() + datetime.timedelta(hours=7)
jam_angka = waktu_wib.hour

if 5 <= jam_angka < 11:
    sapaan = "Selamat Pagi 🌅"
elif 11 <= jam_angka < 15:
    sapaan = "Selamat Siang ☀️"
elif 15 <= jam_angka < 18:
    sapaan = "Selamat Sore 🌇"
else:
    sapaan = "Selamat Malam 🌙"

# Tampilan Judul
st.title(f"📸 {sapaan}")
st.subheader("Sistem Absensi Foto Real-Time")

# Daftar Nama Tim
daftar_nama = [
    "Diana Lestari", "Tuhfah Aqdah Agna", "Dini Atsqiani", 
    "Leily Chusnul Makrifah", "Mochamad Fajar Elhaitami", 
    "Muhammad Farsya Indrawan", "M. Ridho Anwar", "Bebri Ananda Sinukaban"
]

# --- 3. KONEKSI GOOGLE SHEETS ---
# Pastikan konfigurasi Service Account sudah ada di Streamlit Cloud Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

tab1, tab2 = st.tabs(["📍 Presensi", "📊 Rekap Data"])

with tab1:
    nama_pilihan = st.selectbox("Pilih Nama Anda", daftar_nama)
    foto = st.camera_input("Ambil Foto Wajah")

    if st.button("Kirim Absen"):
        if foto is not None:
            with st.spinner("Sedang memproses... Mohon tunggu."):
                try:
                    # A. Upload Foto ke ImgBB
                    files = {"image": foto.getvalue()}
                    response_img = requests.post(f"https://api.imgbb.com/1/upload?key={API_IMGBB}", files=files)
                    link_foto = response_img.json()["data"]["url"]

                    # B. Ambil Waktu Saat Klik Tombol (WIB)
                    waktu_klik = datetime.datetime.now() + datetime.timedelta(hours=7)
                    tgl = waktu_klik.strftime("%Y-%m-%d")
                    jam = waktu_klik.strftime("%H:%M:%S")

                    # C. Ambil Data Lama agar Tidak Menimpa
                    try:
                        df_lama = conn.read().dropna(how="all")
                    except:
                        # Jika sheet masih kosong, buat kolom header
                        df_lama = pd.DataFrame(columns=["Nama", "Tanggal", "Jam", "Foto_Link", "Preview_Foto"])

                    # D. Buat Baris Baru
                    data_baru = pd.DataFrame([{
                        "Nama": nama_pilihan,
                        "Tanggal": tgl,
                        "Jam": jam,
                        "Foto_Link": link_foto,
                        "Preview_Foto": f'=IMAGE("{link_foto}")'
                    }])

                    # E. Gabungkan & Update ke Google Sheets
                    df_final = pd.concat([df_lama, data_baru], ignore_index=True)
                    conn.update(data=df_final)

                    st.success(f"✅ Berhasil! {nama_pilihan} tercatat pada {jam} WIB.")
                except Exception as e:
                    st.error(f"Terjadi kesalahan: {e}")
        else:
            st.warning("⚠️ Silakan ambil foto terlebih dahulu sebelum mengirim.")

with tab2:
    st.subheader("Data Absensi Terkini")
    # Membaca ulang data terbaru dari Google Sheets
    try:
        data_rekap = conn.read().dropna(how="all")
        st.dataframe(data_rekap, use_container_width=True)
    except:
        st.info("Belum ada data absensi.")

