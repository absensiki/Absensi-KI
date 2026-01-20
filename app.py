import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import requests
# Tambahkan ini di bagian atas dekat import
import time

# Jika jam di website meleset, kita tambahkan offset 7 jam untuk WIB
jam_sekarang = (datetime.datetime.now() + datetime.timedelta(hours=7)).hour
# --- KONFIGURASI ---
# GANTI DENGAN DATA ANDA
LINK_SHEET = "https://docs.google.com/spreadsheets/d/1ATGIL-GD0mQHIFq6ziitTpVk12WUCNyYHMeNswM6ngI/edit?gid=0#gid=0"
API_IMGBB = "45ef23a8d4da7b8ed4acfea2a00c76a7"
# Atur zona waktu ke WIB (Tambah 7 jam dari waktu server UTC)
waktu_wib = datetime.datetime.now() + datetime.timedelta(hours=7)
jam_sekarang = waktu_wib.hour

# Tentukan sapaan
if 5 <= jam_sekarang < 11:
    sapaan = "Selamat Pagi 🌅"
elif 11 <= jam_sekarang < 15:
    sapaan = "Selamat Siang ☀️"
elif 15 <= jam_sekarang < 18:
    sapaan = "Selamat Sore 🌇"
else:
    sapaan = "Selamat Malam 🌙"

st.set_page_config(page_title="Absensi Tim KI", layout="centered")
st.title(f"📸 {sapaan}") # Judul berubah otomatis
st.set_page_config(page_title="Absensi Tim KI", layout="centered")

# Daftar Nama
daftar_nama = [
    "Diana Lestari", "Tuhfah Aqdah Agna", "Dini Atsqiani", 
    "Leily Chusnul Makrifah", "Mochamad Fajar Elhaitami", 
    "Muhammad Farsya Indrawan", "M. Ridho Anwar", "Bebri Ananda Sinukaban"
]

# Koneksi GSheets
conn = st.connection("gsheets", type=GSheetsConnection)


st.subheader("Sistem Absensi Konsultan Individu Dirjen Prasarana Strategis Banten")

tab1, tab2 = st.tabs(["Presensi", "Rekap Data"])

with tab1:
    nama = st.selectbox("Pilih Nama", daftar_nama)
    foto = st.camera_input("Ambil Foto Wajah")

    if st.button("Kirim Absen"):
        if foto:
            with st.spinner("Proses menyimpan..."):
                # 1. Upload ke ImgBB
                files = {"image": foto.getvalue()}
                resp = requests.post(f"https://api.imgbb.com/1/upload?key={API_IMGBB}", files=files)
                link_foto = resp.json()["data"]["url"]

                # 2. Data Waktu
                waktu = datetime.datetime.now()
                tgl = waktu.strftime("%Y-%m-%d")
                jam = waktu.strftime("%H:%M:%S")

                # 3. Update Sheet
                df_lama = conn.read(spreadsheet=LINK_SHEET).dropna(how="all")
                data_baru = pd.DataFrame([{"Nama": nama, "Tanggal": tgl, "Jam": jam, "Foto_Link": link_foto, "Preview_Foto": f'=IMAGE("{link_foto}")'}])
                df_final = pd.concat([df_lama, data_baru], ignore_index=True)
                conn.update(spreadsheet=LINK_SHEET, data=df_final)

                st.success(f"Berhasil Absen, {nama}!")
        else:
            st.error("Ambil foto dulu!")

with tab2:
    st.subheader("Data Absen Terkini")
    rekap = conn.read(spreadsheet=LINK_SHEET)
    st.dataframe(rekap)












