# User Guide - Demand Forecasting System

Panduan penggunaan sistem forecasting untuk end users.

## 📖 Pengenalan

Sistem Demand Forecasting adalah aplikasi web untuk memprediksi kebutuhan (demand) produk berdasarkan data historis menggunakan Machine Learning.

### Fitur Utama
- Upload data CSV historis
- Konfigurasi parameter forecast
- Real-time progress monitoring
- Download hasil dalam format CSV
- Lihat riwayat forecast sebelumnya

## 🚀 Cara Menggunakan

### 1️⃣ Akses Aplikasi

Buka browser dan akses:
```
http://[server-ip-address]
```

Anda akan melihat halaman Dashboard.

### 2️⃣ Persiapkan Data CSV

Data harus dalam format CSV dengan **kolom wajib**:

| Kolom | Deskripsi | Contoh |
|-------|-----------|--------|
| `date` | Tanggal transaksi | 2024-01-15 atau 15/01/2024 |
| `partnumber` | Kode part/produk | PART-001 |
| `site_code` | Kode lokasi/site | IEL-ST-KDI |
| `demand_qty` | Jumlah demand | 100 |

**Contoh data CSV:**
```csv
date,partnumber,site_code,demand_qty
2024-01-01,PART-001,IEL-ST-KDI,50
2024-01-02,PART-001,IEL-ST-KDI,75
2024-01-03,PART-001,IEL-ST-KDI,60
2024-01-01,PART-002,IEL-MU-SFI,30
```

**Tips:**
- Minimal 3 bulan data historis untuk hasil yang baik
- Format tanggal konsisten di seluruh file
- Tidak ada nilai kosong di kolom wajib

### 3️⃣ Upload Data

1. Di halaman Dashboard, klik area upload atau drag file CSV
2. Sistem akan validasi file:
   - ✅ Format harus CSV
   - ✅ Ukuran maksimal 50MB
3. Jika valid, nama file akan muncul

### 4️⃣ Konfigurasi Forecast

#### **Forecast Horizon**
Jumlah hari ke depan yang akan diprediksi.
- **Rentang**: 1 - 90 hari
- **Rekomendasi**: 7 hari untuk weekly planning, 30 hari untuk monthly planning
- **Contoh**: Isi `7` untuk forecast 1 minggu ke depan

#### **Site Codes**
Filter site yang akan di-forecast.
- **Kosongkan**: Forecast untuk semua site di data
- **Isi spesifik**: Masukkan kode site, pisahkan dengan koma
- **Contoh**: `IEL-ST-KDI,IEL-MU-SFI` (forecast hanya 2 site ini)

#### **Zero Threshold**
Nilai minimum prediksi. Prediksi di bawah threshold akan diset ke 0.
- **Rentang**: 0 - 10
- **Default**: 0.5
- **Fungsi**: Menghilangkan prediksi yang terlalu kecil (noise)
- **Contoh**: Jika threshold = 0.5, prediksi 0.3 akan menjadi 0

#### **Rounding Mode**
Cara pembulatan hasil forecast.
- **Half Up**: 0.5 ke atas dibulatkan naik (0.5→1, 1.5→2)
- **Round**: Pembulatan standar (0.4→0, 0.6→1)
- **Ceiling**: Selalu dibulatkan ke atas (0.1→1, 1.1→2)
- **Floor**: Selalu dibulatkan ke bawah (0.9→0, 1.9→1)

**Rekomendasi**: Gunakan **Half Up** untuk hasil konservatif.

#### **Format Tanggal**
Format parsing tanggal di CSV Anda.
- **Day First (DD/MM/YYYY)**: Format Indonesia (15/01/2024)
- **Month First (MM/DD/YYYY)**: Format US (01/15/2024)

**Tip**: Jika hasil forecast error "tanggal gagal parse", coba ganti setting ini.

### 5️⃣ Jalankan Forecast

1. Pastikan file sudah diupload
2. Konfigurasi sudah diatur
3. Klik tombol **"Jalankan Forecast"** (biru, dengan icon roket)
4. Tunggu proses selesai

**Progress Indicator:**
- Progress bar akan update otomatis setiap 2 detik
- Status akan berubah: QUEUED → PROCESSING → COMPLETED
- Waktu proses tergantung ukuran data (umumnya 1-5 menit)

### 6️⃣ Download Hasil

Setelah status **COMPLETED**:

1. Scroll ke bagian **Status Forecast**
2. Lihat metrics model (MAE, RMSE, MAPE)
3. Klik tombol **"Download Hasil"**
4. File CSV akan terdownload

**Format Hasil CSV:**

| Kolom | Deskripsi |
|-------|-----------|
| `date` | Tanggal forecast |
| `partnumber` | Kode part |
| `site_code` | Kode site |
| `forecast_qty` | Prediksi final (sudah dibulatkan) |
| `forecast_qty_raw` | Prediksi setelah threshold |
| `forecast_qty_raw_model` | Prediksi mentah dari model |

**Kolom yang paling penting**: `forecast_qty` (gunakan ini untuk planning)

### 7️⃣ Lihat Riwayat

1. Klik menu **"Riwayat"** di header
2. Akan muncul tabel semua forecast jobs
3. Fitur tersedia:
   - **Filter by Status**: QUEUED, PROCESSING, COMPLETED, FAILED
   - **Download**: Download hasil forecast lama
   - **Hapus**: Hapus job yang tidak diperlukan
   - **Refresh**: Update status terbaru

## 📊 Memahami Metrics

Setelah forecast selesai, akan muncul **Metrics Model**:

### MAE (Mean Absolute Error)
- Rata-rata error absolut
- **Semakin kecil semakin baik**
- Satuan sama dengan demand (misalnya unit produk)
- Contoh: MAE = 1.2 berarti rata-rata prediksi meleset 1.2 unit

### RMSE (Root Mean Square Error)
- Akar dari rata-rata kuadrat error
- **Semakin kecil semakin baik**
- Lebih sensitif terhadap outlier dibanding MAE
- Biasanya lebih besar dari MAE

### MAPE% (Mean Absolute Percentage Error)
- Error dalam bentuk persentase
- **Semakin kecil semakin baik**
- Contoh: MAPE = 10% berarti rata-rata prediksi meleset 10% dari aktual
- **Interpretasi**:
  - < 10%: Excellent
  - 10-20%: Good
  - 20-50%: Acceptable
  - > 50%: Poor

### sMAPE% (Symmetric MAPE)
- Versi symmetric dari MAPE
- Lebih adil untuk data dengan rentang nilai besar
- Interpretasi sama dengan MAPE

## ❓ FAQ

### Q: Berapa lama waktu yang dibutuhkan untuk forecast?

**A**: Tergantung ukuran data:
- < 10,000 baris: 1-2 menit
- 10,000 - 50,000 baris: 2-5 menit
- > 50,000 baris: 5-10 menit

### Q: Apakah bisa forecast untuk site baru yang belum ada data?

**A**: Tidak optimal. Sistem memerlukan data historis untuk site tersebut. Jika site baru, hasilnya akan kurang akurat atau bahkan 0.

### Q: Mengapa hasil forecast saya semua 0?

**A**: Kemungkinan penyebab:
1. Data historis site tersebut sangat sedikit/sparse
2. Zero threshold terlalu tinggi (coba turunkan ke 0.1)
3. Site code tidak ada di data historis
4. Data terlalu baru/kurang dari 1 bulan

### Q: Apakah bisa forecast lebih dari 90 hari?

**A**: Secara teknis bisa, tapi tidak direkomendasikan. Semakin jauh forecast, semakin tidak akurat. Maksimal sistem adalah 90 hari.

### Q: Format tanggal di CSV saya campuran, bagaimana?

**A**: Normalkan dulu format tanggal di Excel/spreadsheet sebelum upload. Sistem tidak bisa handle format campuran.

### Q: Apakah bisa export ke Excel?

**A**: Hasil download dalam CSV. Anda bisa buka di Excel dengan:
1. Excel → Data → From Text/CSV
2. Pilih file CSV yang didownload
3. Import

### Q: Kenapa forecast saya FAILED?

**A**: Check detail error di **Status Monitor**. Error umum:
- Format CSV tidak sesuai
- Kolom wajib tidak ada
- Format tanggal salah
- Data corrupt/tidak valid

### Q: Apakah hasil forecast bisa diedit?

**A**: Tidak di sistem. Download CSV lalu edit di Excel jika perlu adjustment manual.

## 💡 Best Practices

### 1. Data Quality
- ✅ Pastikan data bersih (no duplicate, no missing critical columns)
- ✅ Data minimal 3 bulan, ideal 6-12 bulan
- ✅ Update data secara reguler untuk forecast yang akurat

### 2. Konfigurasi
- ✅ Mulai dengan default config dulu
- ✅ Tuning threshold dan rounding sesuai kebutuhan bisnis
- ✅ Horizon disesuaikan dengan planning cycle

### 3. Workflow
- ✅ Download data aktual terbaru dari sistem ERP/database
- ✅ Run forecast di awal periode (misalnya setiap Senin untuk weekly forecast)
- ✅ Compare hasil forecast dengan aktual untuk evaluasi

### 4. Interpretasi Hasil
- ✅ Gunakan `forecast_qty` untuk planning
- ✅ Lihat metrics untuk assess kualitas prediksi
- ✅ Jika MAPE > 50%, cek kualitas data historis

## 🆘 Bantuan

Jika mengalami masalah:

1. **Check Status Monitor** untuk detail error
2. **Lihat FAQ** di atas
3. **Contact IT Support** dengan informasi:
   - Screenshot error
   - File CSV yang digunakan
   - Konfigurasi yang dipilih
   - Job ID dari history

## 📝 Catatan Penting

⚠️ **Data Privacy**: Jangan upload data confidential/sensitive tanpa izin
⚠️ **File Size**: Maksimal 50MB per upload
⚠️ **Concurrent Jobs**: Jika ada banyak user, antri otomatis (FIFO)
⚠️ **Result Retention**: Hasil forecast disimpan, tapi bisa dihapus admin setelah 30 hari

---

**Selamat menggunakan Demand Forecasting System!** 🚀

