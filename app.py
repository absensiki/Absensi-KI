import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import requests

# --- KONFIGURASI API ---
# Pastikan API Key ImgBB Anda benar
API_IMGBB = "45ef23a8d4da7b8ed4acfea2a00c76a7"

st.set_page_config(page_title="Absensi Tim KI", layout="centered")

# --- LOGIKA SAPAAN & WAKTU WIB ---
waktu_wib = datetime.datetime.now() + datetime.timedelta(hours=7)
jam_sekarang = waktu_wib.hour

if 5 <= jam_sekarang < 11:
    sapaan = "Selamat Pagi 🌅"
elif 11 <= jam_sekarang < 15:
    sapaan = "Selamat Siang ☀️"
elif 15 <= jam_sekarang < 18:
    sapaan = "Selamat Sore 🌇"
else:
    sapaan = "Selamat Malam 🌙"

st.title(f"📸 {sapaan}")
st.subheader("Sistem Absensi Foto Real-Time")

# Daftar Nama
daftar_nama = [
    "Diana Lestari", "Tuhfah Aqdah Agna", "Dini Atsqiani", 
    "Leily Chusnul Makrifah", "Mochamad Fajar Elhaitami", 
    "Muhammad Farsya Indrawan", "M. Ridho Anwar", "Bebri Ananda Sinukaban"
]

# Koneksi GSheets (Mengambil data dari Secrets)
conn = st.connection("gsheets", type=GSheetsConnection)

tab1, tab2 = st.tabs(["Presensi", "Rekap Data"])

with tab1:
    nama = st.selectbox("Pilih Nama", daftar_nama)
    foto = st.camera_input("Ambil Foto Wajah")

    if st.button("Kirim Absen"):
        if foto:
            with st.spinner("Sedang memproses absensi..."):
                # 1. Upload ke ImgBB
                files = {"image": foto.getvalue()}
                resp = requests.post(f"https://api.imgbb.com/1/upload?key={API_IMGBB}", files=files)
                link_foto = resp.json()["data"]["url"]

                # 2. Data Waktu WIB
                tgl = waktu_wib.strftime("%Y-%m-%d")
                jam = waktu_wib.strftime("%H:%M:%S")

                # 3. Baca Data Lama & Tambahkan Baris Baru
                try:
                    # Membaca data dan membersihkan baris kosong
                    df_lama = conn.read()
                    df_lama = df_lama.dropna(how="all")
                except:
                    df_lama = pd.DataFrame(columns=["Nama", "Tanggal", "Jam", "Foto_Link", "Preview_Foto"])

                # Buat baris baru
                data_baru = pd.DataFrame([{
                    "Nama": nama, 
                    "Tanggal": tgl, 
                    "Jam": jam, 
                    "Foto_Link": link_foto, 
                    "Preview_Foto": f'=IMAGE("{link_foto}")'
                }])

                # Gabungkan data (Append)
                df_final = pd.concat([df_lama, data_baru], ignore_index=True)

                # 4. Kirim ke Google Sheets
                conn.update(data=df_final)
                st.success(f"Berhasil Absen, {nama}! (Tercatat jam {jam})")
        else:
            st.error("Silakan ambil foto terlebih dahulu!")

with tab2:
    st.subheader("Data Absen Terkini")
    rekap = conn.read()
    st.dataframe(rekap)
