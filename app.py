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
            with st.spinner("Sedang memproses absensi..."):
                # 1. Upload ke ImgBB
                files = {"image": foto.getvalue()}
                resp = requests.post(f"https://api.imgbb.com/1/upload?key={API_IMGBB}", files=files)
                link_foto = resp.json()["data"]["url"]

                # 2. Ambil Waktu WIB (Tambah 7 Jam)
                waktu_wib = datetime.datetime.now() + datetime.timedelta(hours=7)
                tgl = waktu_wib.strftime("%Y-%m-%d")
                jam = waktu_wib.strftime("%H:%M:%S")

                # 3. Ambil data yang sudah ada di Google Sheets
                # Kita tambahkan .dropna(how="all") agar baris kosong tidak ikut terbaca
                try:
                    df_lama = conn.read()
                    df_lama = df_lama.dropna(how="all") 
                except:
                    df_lama = pd.DataFrame(columns=["Nama", "Tanggal", "Jam", "Foto_Link", "Preview_Foto"])

                # 4. Buat Baris Baru
                data_baru = pd.DataFrame([{
                    "Nama": nama,
                    "Tanggal": tgl,
                    "Jam": jam,
                    "Foto_Link": link_foto,
                    "Preview_Foto": f'=IMAGE("{link_foto}")'
                }])

                # 5. Gabungkan (Append) data lama dengan data baru
                # Ini yang memastikan data bertambah di bawah, bukan menimpa
                df_final = pd.concat([df_lama, data_baru], ignore_index=True)

                # 6. Kirim kembali ke Google Sheets
                conn.update(data=df_final)

                st.success(f"✅ Berhasil! {nama} sudah absen pada jam {jam}")
        else:
            st.error("❌ Silakan ambil foto terlebih dahulu!")
with tab2:
    st.subheader("Data Absen Terkini")
    rekap = conn.read(spreadsheet=LINK_SHEET)
    st.dataframe(rekap)














