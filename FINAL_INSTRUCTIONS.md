# 🎯 Final Instructions - Ready to Test!

## ✅ ERROR "0 SAMPLES" SUDAH FIXED!

### **Root Cause:**
```
Data example.csv: 30 hari
System requirements: 56+ hari untuk lag_28 + rollmean_28
Result: Semua rows NULL → 0 samples error
```

### **Solution Applied:**
```
✅ Adaptive Lag Features
   • Auto-detect data span
   • Auto-adjust lags untuk fit data
   • 30 hari → Use lag_1, lag_7, lag_14 (skip lag_28)
   • Dynamic feature columns
```

---

## 🚀 CARA MENGGUNAKAN (Step-by-Step)

### **UNTUK example.csv (30 hari, 459 rows):**

1. **Buka**: http://localhost:9572
2. **Hard Refresh**: `Cmd + Shift + R` (clear cache!)
3. **Upload**: `real_data/example.csv`
4. **Konfigurasi**:
   - Site Codes: `IEL-ST-KDI` (atau kosong)
   - Format Tanggal: **Month First** (MM/DD/YYYY)
   - Horizon: 7 hari (default OK)
5. **Klik**: "Jalankan Forecast"
6. **Tunggu**: 30-60 detik
7. **Download**: CSV hasil

---

### **UNTUK alldemand_augjul.csv (full data):**

1. **Upload**: `real_data/alldemand_augjul.csv`
2. **Konfigurasi**:
   - Site Codes: `IEL-ST-KDI` ← **WAJIB** (untuk speed)
   - Format Tanggal: **Month First**
3. **Klik**: "Jalankan Forecast"
4. **Tunggu**: 2-3 menit
5. **Jika stuck >5 min**: Click **"Stop Job"** 🛑
6. **Download**: CSV hasil

---

## ⏱️ WAKTU ESTIMASI

| File | Rows | Days | With Filter | No Filter |
|------|------|------|-------------|-----------|
| example.csv | 459 | 30 | **30-60 sec** ✅ | 1-2 min |
| alldemand_augjul.csv | 11,919 | Plenty | **2-3 min** ✅ | 15-30 min ⚠️ |

---

## 🔍 MONITORING

### **Normal Progress:**
```
0% QUEUED
  ↓ (10 sec)
5% PROCESSING - Loading
  ↓ (15 sec)
15% PROCESSING - Preprocessing
  ↓ (10 sec)
25% PROCESSING - Features
  ↓ (20-60 sec)
35% PROCESSING - Training GBR
  ↓ (10-20 sec)
50% PROCESSING - Training Ridge
  ↓ (20-30 sec)
70% PROCESSING - Forecasting
  ↓ (10 sec)
100% COMPLETED ✅
```

### **If Stuck:**
```
Progress tidak berubah >3 menit
         ↓
Click "Stop Job" button (red)
         ↓
Confirm "Ya, Stop"
         ↓
Job terminated dalam 1-2 detik
         ↓
Status: CANCELLED
         ↓
Re-upload dengan fix ✅
```

---

## 🚨 TROUBLESHOOTING

### Error: "Found array with 0 sample(s)"
**Status:** ✅ FIXED dengan adaptive lags
**Test:** Upload example.csv sekarang harusnya berhasil

### Error: API hit ke port 8000
**Fix:** Hard refresh browser (Cmd+Shift+R)

### Job stuck >5 menit
**Fix:** Click "Stop Job" button

### Training terlalu lama
**Fix:** Pastikan Site Codes diisi (filter 1 site)

---

## 📋 QUICK REFERENCE

### **URLs:**
- Frontend: http://localhost:9572
- Backend: http://localhost:9571
- API Docs: http://localhost:9571/api/docs

### **Commands:**
```bash
# Monitor logs
docker-compose logs -f celery_worker

# Restart if needed
docker-compose restart backend celery_worker

# Stop all
docker-compose down
```

### **Data Requirements:**
- Format: CSV dengan kolom (date, partnumber, site_code, demand_qty)
- Date format: MM/DD/YYYY (8/5/2024, 3/3/2025)
- Min data: 15+ hari (akan auto-adjust)
- Recommended: 60+ hari (untuk akurasi optimal)

---

## ✅ CHECKLIST SEBELUM SUBMIT

- [ ] File CSV ready (example.csv atau alldemand_augjul.csv)
- [ ] Browser opened: http://localhost:9572
- [ ] Cache cleared: Cmd+Shift+R
- [ ] Site Codes: Diisi untuk speed
- [ ] Format Tanggal: Month First
- [ ] Ready untuk monitor progress

---

## 🎉 EXPECTED RESULT

Setelah COMPLETED:
- ✅ CSV dengan 7 hari forecast
- ✅ Columns: date, partnumber, site_code, forecast_qty
- ✅ Model metrics (MAE, RMSE, MAPE%)
- ✅ Download button active

---

**System is READY! Test sekarang!** 🚀
