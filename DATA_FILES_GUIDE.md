# 📁 Data Files Guide

## 📊 SAMPLE FILES TERSEDIA

### 1️⃣ **sample_optimal.csv** ⭐ RECOMMENDED!

**Path:** `/Users/falaqmsi/Documents/GitHub/forecast/sample_optimal.csv`

**Specifications:**
```
✅ Rows:        1,022 rows
✅ Date Range:  7/1/2024 - 9/9/2024 (90+ hari)
✅ Sites:       3 (IEL-ST-KDI, IEL-MU-SFI, Sofifi)
✅ Parts:       13 partnumbers
✅ Format:      MM/DD/YYYY tanpa leading zero
✅ Features:    Weekly patterns, trend, realistic noise
```

**Distribution:**
- IEL-ST-KDI: 399 rows (5 parts)
- Sofifi: 317 rows (4 parts)
- IEL-MU-SFI: 306 rows (4 parts)

**Kapan Pakai:**
- ✅ Testing sistem pertama kali
- ✅ Punya 90+ hari → All lag features works
- ✅ Quick test (30-60 detik dengan filter)
- ✅ Tidak ada error "0 samples"

**Expected Time:**
- With filter (1 site): **30-60 seconds** ✅
- Without filter (all): **1-2 minutes**

---

### 2️⃣ **example.csv**

**Path:** `/Users/falaqmsi/Documents/GitHub/forecast/real_data/example.csv`

**Specifications:**
```
⚠️  Rows:        459 rows
⚠️  Date Range:  8/5/2024 - 9/4/2024 (30 hari)
✅ Sites:       4 (IEL-KS-ANGSANA, IEL-ST-KDI, IEL-MU-SFI, Sofifi)
✅ Parts:       Many partnumbers
✅ Format:      MM/DD/YYYY tanpa leading zero
```

**Kapan Pakai:**
- ⚠️  Small dataset (30 hari)
- ⚠️  Akan pakai adaptive lags (lag_1, lag_7, lag_14 only)
- ✅ Sudah di-fix dengan adaptive features
- ✅ Bisa dipakai untuk testing

**Expected Time:**
- With filter: **30-60 seconds**
- Without filter: **1-2 minutes**

**Note:** Akurasi mungkin lebih rendah karena data terbatas

---

### 3️⃣ **alldemand_augjul.csv** (PRODUCTION DATA)

**Path:** `/Users/falaqmsi/Documents/GitHub/forecast/real_data/alldemand_augjul.csv`

**Specifications:**
```
✅ Rows:        11,919 rows (LARGE!)
✅ Sites:       13 sites
⚠️  Parts:       2,070 partnumbers (VERY MANY!)
✅ Format:      MM/DD/YYYY tanpa leading zero
```

**Distribution:**
- IEL-ST-KDI: 3,336 rows (28%)
- Sofifi: 2,291 rows (19%)
- Kendari: 1,295 rows (11%)
- ... 10 more sites

**Kapan Pakai:**
- ✅ Production data (real demand)
- ⚠️  MUST use site filter (avoid slow training)
- ✅ Good accuracy (plenty of data)

**Expected Time:**
- **With filter (1 site): 2-3 minutes** ✅ RECOMMENDED
- Without filter (all): 15-30 minutes ⚠️ SLOW!

**Important:**
- **WAJIB isi Site Codes** (pilih 1-2 site)
- Jangan upload tanpa filter (akan sangat lambat!)

---

### 4️⃣ **sample_data.csv** (BASIC SAMPLE)

**Path:** `/Users/falaqmsi/Documents/GitHub/forecast/sample_data.csv`

**Specifications:**
```
✅ Rows:        60 rows
✅ Date Range:  60 hari (Feb-Mar 2024)
✅ Sites:       1 (PART-001)
✅ Parts:       1
✅ Format:      YYYY-MM-DD (ISO format)
```

**Kapan Pakai:**
- ✅ Quick test API functionality
- ✅ Simple data untuk debugging
- ⚠️  Format berbeda (ISO vs MM/DD/YYYY)

**Expected Time:**
- **< 30 seconds**

---

## 🎯 REKOMENDASI PENGGUNAAN

### **Untuk Testing Pertama Kali:**
```
File: sample_optimal.csv ⭐
Config: Site = IEL-ST-KDI, Format = Month First
Time: 30-60 seconds
Result: Perfect test! ✅
```

### **Untuk Testing Small Data:**
```
File: example.csv
Config: Site = IEL-ST-KDI, Format = Month First  
Time: 30-60 seconds
Result: OK tapi adaptive lags (akurasi lower)
```

### **Untuk Production/Real Forecast:**
```
File: alldemand_augjul.csv
Config: Site = IEL-ST-KDI (WAJIB!), Format = Month First
Time: 2-3 minutes
Result: Production ready! ✅
```

---

## 📋 FILE FORMAT REQUIREMENTS

### **Required Columns:**
```csv
demand_qty,date,partnumber,site_code
```

### **Date Format Supported:**
```
✅ 3/3/2025       (no leading zero)
✅ 03/03/2025     (with leading zero)
✅ 8/5/2024       (no leading zero)
✅ 2024-08-05     (ISO format)
```

### **Data Requirements:**
- **Minimal**: 15+ hari (akan adaptive)
- **Recommended**: 60+ hari (good accuracy)
- **Optimal**: 90+ hari (best accuracy)

---

## 🧪 TESTING MATRIX

| File | Rows | Days | Partnumbers | Filter Site? | Time | Best For |
|------|------|------|-------------|--------------|------|----------|
| sample_optimal.csv | 1K | 90 | 13 | Optional | 30-60s | **Testing** ⭐ |
| example.csv | 459 | 30 | Many | Yes | 30-60s | Small data |
| sample_data.csv | 60 | 60 | 1 | No | <30s | Quick test |
| alldemand_augjul.csv | 12K | Plenty | 2070 | **REQUIRED** | 2-3min | **Production** |

---

## 🚀 QUICK START - RECOMMENDED PATH

### **Step 1: Test dengan sample_optimal.csv**
```bash
1. Upload: sample_optimal.csv
2. Site: IEL-ST-KDI
3. Format: Month First
4. Run → 30-60 seconds
5. Verify: Download & check hasil ✅
```

### **Step 2: Test dengan example.csv**
```bash
1. Upload: example.csv
2. Site: IEL-ST-KDI
3. Format: Month First
4. Run → 30-60 seconds
5. Verify: Adaptive lags work ✅
```

### **Step 3: Production dengan alldemand_augjul.csv**
```bash
1. Upload: alldemand_augjul.csv
2. Site: IEL-ST-KDI ← WAJIB!
3. Format: Month First
4. Run → 2-3 minutes
5. Download real forecast ✅
```

---

## 📝 NOTES

### **Format Tanggal:**
- Semua file pakai **MM/DD/YYYY** format
- Select **"Month First"** di UI
- System auto-handle no leading zero (3/3/2025)

### **Site Filtering:**
- **sample_optimal.csv**: Optional (data kecil)
- **example.csv**: Recommended (faster)
- **alldemand_augjul.csv**: **MANDATORY** (avoid slow training)

### **Expected Metrics:**
- MAE: 1-5 (tergantung data)
- MAPE: 10-30% (good)
- sMAPE: 15-40% (acceptable)

---

## ✅ READY TO TEST!

**Recommended:** Start dengan `sample_optimal.csv` ⭐

**File location:** `/Users/falaqmsi/Documents/GitHub/forecast/sample_optimal.csv`

**Upload di:** http://localhost:9572

**Expected:** 30-60 seconds, no errors! 🚀
