# 🧪 Testing Guide - Forecast System

## ✅ SISTEM SUDAH READY!

### 🌐 URLs
- **Frontend**: http://localhost:9572
- **Backend API**: http://localhost:9571
- **API Docs**: http://localhost:9571/api/docs

---

## 📊 DATA REAL ANDA

### File Info
- **Location**: `/Users/falaqmsi/Documents/GitHub/forecast/real_data/alldemand_augjul.csv`
- **Rows**: 11,919
- **Sites**: 13 sites
- **Partnumbers**: 2,070 unique
- **Date Format**: MM/DD/YYYY (contoh: 8/5/2024, 3/3/2025)

### Top Sites (by volume)
1. **IEL-ST-KDI**: 3,336 rows (28%) ← **RECOMMENDED untuk test pertama**
2. **Sofifi**: 2,291 rows (19%)
3. **Kendari**: 1,295 rows (11%)
4. **IEL-TMSB2**: 1,163 rows
5. **IEL-MU-SFI**: 1,005 rows

---

## 🚀 CARA TEST (Step-by-Step)

### STEP 1: Buka Frontend
```
http://localhost:9572
```

### STEP 2: Hard Refresh (PENTING!)
```
Mac: Cmd + Shift + R
Windows: Ctrl + Shift + R
```
**Kenapa?** Clear browser cache supaya hit ke port 9571 (bukan 8000)

### STEP 3: Upload File
- Klik area upload atau drag file
- Pilih: `real_data/alldemand_augjul.csv`
- File size: 427KB ✅

### STEP 4: Konfigurasi

#### ⚠️ WAJIB DIISI (untuk avoid slow training):

| Setting | Value | Penjelasan |
|---------|-------|------------|
| **Site Codes** | `IEL-ST-KDI` | Filter 1 site (cepat: 2-3 min) |
| **Format Tanggal** | `Month First` | Data pakai MM/DD/YYYY |

#### ✅ Bisa Default:

| Setting | Default | OK? |
|---------|---------|-----|
| Forecast Horizon | 7 hari | ✅ |
| Zero Threshold | 0.5 | ✅ |
| Rounding Mode | Half Up | ✅ |

### STEP 5: Run Forecast
- Klik **"Jalankan Forecast"** (button biru)
- Progress bar akan muncul
- Status akan update otomatis

### STEP 6: Monitor Progress
Expected flow:
```
QUEUED (0%) 
  ↓ (10 sec)
PROCESSING - Loading (5%)
  ↓ (15 sec)
PROCESSING - Preprocessing (15%)
  ↓ (10 sec)
PROCESSING - Features (25%)
  ↓ (20 sec)
PROCESSING - Training (35%)
  ↓ (60-90 sec) ← LONGEST PART
PROCESSING - Forecasting (70%)
  ↓ (30 sec)
COMPLETED (100%) ✅
```

**Total time**: 2-3 menit

### STEP 7: Download Hasil
- Button **"Download Hasil"** akan aktif
- Klik untuk download CSV
- File name: `forecast_result_[job_id].csv`

---

## 📋 OUTPUT CSV FORMAT

| Column | Description |
|--------|-------------|
| `date` | Tanggal forecast (7 hari ke depan) |
| `partnumber` | Kode part |
| `site_code` | Kode site |
| `forecast_qty` | **Prediksi final** (sudah dibulatkan) ← **USE THIS** |
| `forecast_qty_raw` | Prediksi setelah threshold |
| `forecast_qty_raw_model` | Prediksi mentah dari model |

**Kolom untuk operational planning**: `forecast_qty`

---

## 🔍 TROUBLESHOOTING

### Issue: API hit ke port 8000 (bukan 9571)
**Fix:**
```
Browser → Hard refresh (Cmd+Shift+R)
Atau: Incognito mode (Cmd+Shift+N)
```

### Issue: Job stuck di PROCESSING
**Cek:**
```bash
docker-compose logs -f celery_worker
```
**Fix:**
```bash
docker-compose restart celery_worker
```

### Issue: "Tanggal gagal parse"
**Check:**
- Setting "Format Tanggal" harus "Month First" (MM/DD/YYYY)
- Data Anda: 8/5/2024 = August 5, 2024 (Month First)

### Issue: Training terlalu lama (>5 min)
**Fix:**
- Pastikan **Site Codes** sudah diisi (filter 1 site)
- Jangan kosongkan Site Codes (akan process all 2070 partnumbers!)

---

## 📈 TESTING SCENARIOS

### Scenario 1: Quick Test (Recommended)
```
File: real_data/alldemand_augjul.csv
Site Codes: IEL-ST-KDI
Expected: 2-3 minutes
Output: ~7 rows × partnumbers di site IEL-ST-KDI
```

### Scenario 2: Multiple Sites (Sequential)
```
Run 1: Site = IEL-ST-KDI    → 2-3 min
Run 2: Site = Sofifi        → 2-3 min
Run 3: Site = Kendari       → 2-3 min

Total: 6-9 minutes untuk 70% of data
```

### Scenario 3: All Sites (Slow)
```
File: real_data/alldemand_augjul.csv
Site Codes: (kosong - all sites)
Expected: 15-30 minutes ⚠️
⚠️ NOT RECOMMENDED untuk test pertama
```

---

## ✅ CHECKLIST SEBELUM SUBMIT

- [ ] File uploaded: alldemand_augjul.csv
- [ ] **Site Codes**: IEL-ST-KDI (diisi!)
- [ ] **Format Tanggal**: Month First (dipilih!)
- [ ] Browser cache cleared (hard refresh)
- [ ] Network tab open (F12) untuk monitoring
- [ ] Ready untuk tunggu 2-3 menit

---

## 🎉 EXPECTED SUCCESS

Setelah COMPLETED, Anda akan lihat:
- ✅ Status: COMPLETED (100%)
- ✅ Model metrics (MAE, RMSE, MAPE%)
- ✅ Download button aktif
- ✅ CSV hasil tersedia

---

**Good luck! System sudah fully optimized untuk data Anda!** 🚀
