import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import requests

# --- KONFIGURASI ---
API_IMGBB = "45ef23a8d4da7b8ed4acfea2a00c76a7"

st.set_page_config(page_title="Absensi Tim KI", layout="centered")

# --- WAKTU WIB UNTUK JUDUL & INPUT ---
waktu_wib = datetime.datetime.now() + datetime.timedelta(hours=7)
jam_angka = waktu_wib.hour

if 5 <= jam_angka < 11:
    sapaan = "Halo, Selamat Pagi 🌅"
elif 11 <= jam_angka < 15:
    sapaan = "Halo, Selamat Siang ☀️"
elif 15 <= jam_angka < 18:
    sapaan = "Halo, Selamat Sore 🌇"
else:
    sapaan = "Halo, Selamat Malam 🌙"

st.title(f"{sapaan}")
st.subheader("Absensi KI Satker PPS Banten")

daftar_nama = [
    "Diana Lestari", "Tuhfah Aqdah Agna", "Dini Atsqiani", 
    "Leily Chusnul Makrifah", "Mochamad Fajar Elhaitami", 
    "Muhammad Farsya Indrawan", "M. Ridho Anwar", "Bebri Ananda Sinukaban"
]

conn = st.connection("gsheets", type=GSheetsConnection)

tab1, tab2 = st.tabs(["📍 Presensi", "📊 Rekap Data"])

with tab1:
    nama_pilihan = st.selectbox("Pilih Nama Anda", daftar_nama)
    foto = st.camera_input("Ambil Foto Wajah")

    if st.button("Kirim Absen"):
        if foto is not None:
            with st.spinner("Sedang memproses..."):
                # 1. Upload ke ImgBB
                files = {"image": foto.getvalue()}
                resp = requests.post(f"https://api.imgbb.com/1/upload?key={API_IMGBB}", files=files)
                link_foto = resp.json()["data"]["url"]

                # 2. Ambil Waktu WIB Persis Saat Klik
                waktu_klik = datetime.datetime.now() + datetime.timedelta(hours=7)
                tgl = waktu_klik.strftime("%Y-%m-%d")
                jam = waktu_klik.strftime("%H:%M:%S")

                # 3. Baca & Update Data
                try:
                    df_lama = conn.read(ttl=0).dropna(how="all")
                except:
                    df_lama = pd.DataFrame(columns=["Nama", "Tanggal", "Jam", "Foto_Link", "Preview_Foto"])

                data_baru = pd.DataFrame([{
                    "Nama": nama_pilihan,
                    "Tanggal": tgl,
                    "Jam": jam,
                    "Foto_Link": link_foto,
                    "Preview_Foto": f'=IMAGE("{link_foto}")'
                }])

                df_final = pd.concat([df_lama, data_baru], ignore_index=True)
                conn.update(data=df_final)
                
                # Menghapus cache agar data terbaru langsung muncul di Tab Rekap
                st.cache_data.clear()
                st.success(f"✅ Berhasil! {nama_pilihan} tercatat jam {jam} WIB.")
        else:
            st.warning("Silakan ambil foto terlebih dulu.")

with tab2:
    st.subheader("Data Absensi Terkini (WIB)")
    # Menggunakan ttl=0 agar selalu mengambil data paling baru dari Sheets
    try:
        data_rekap = conn.read(ttl=0).dropna(how="all")
        st.dataframe(data_rekap, use_container_width=True)
    except:
        st.info("Belum ada data.")






