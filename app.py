import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import requests

# --- KONFIGURASI ---
# GANTI DENGAN DATA ANDA
LINK_SHEET = "https://docs.google.com/spreadsheets/d/1ATGIL-GD0mQHIFq6ziitTpVk12WUCNyYHMeNswM6ngI/edit?gid=0#gid=0"
API_IMGBB = "45ef23a8d4da7b8ed4acfea2a00c76a7"

st.set_page_config(page_title="Absensi Tim 8", layout="centered")

# Daftar Nama
daftar_nama = [
    "Diana Lestari", "Tuhfah Aqdah Agna", "Dini Atsqiani", 
    "Leily Chusnul Makrifah", "Mochamad Fajar Elhaitami", 
    "Muhammad Farsya Indrawan", "M. Ridho Anwar", "Bebri Ananda Sinukaban"
]

# Koneksi GSheets
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("📸 Absensi Foto Real-Time")

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
