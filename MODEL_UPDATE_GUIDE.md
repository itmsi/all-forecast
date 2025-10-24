# 🔧 Panduan Update Model & Rumus Forecasting

## 📁 File-File yang Perlu Diubah

### 1. **`backend/app/core/ml_engine.py`** - FILE UTAMA
**Untuk mengubah:**
- Algoritma ML (Ridge → Random Forest, XGBoost, dll)
- Parameter model (alpha, n_estimators, dll)
- Pipeline preprocessing
- Logika training dan selection

**Contoh perubahan:**
```python
# Mengubah dari Ridge ke Random Forest
"RandomForest": Pipeline([
    ("prep", preprocess_sparse),
    ("reg", RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        random_state=self.random_state
    ))
])

# Mengubah parameter Ridge
"Ridge_log": Pipeline([
    ("prep", preprocess_sparse),
    ("reg", TTR(
        regressor=Ridge(alpha=0.1, random_state=self.random_state),  # alpha dari 1.0 ke 0.1
        func=np.log1p, inverse_func=np.expm1
    ))
])
```

### 2. **`backend/app/core/preprocessing.py`** - FEATURE ENGINEERING
**Untuk mengubah:**
- Lag features (1,7,14,28 → 1,3,7,14,21,28)
- Rolling windows (7,14,28 → 3,7,14,21,30)
- Calendar features baru
- Outlier handling

**Contoh perubahan:**
```python
# Menambah lag features baru
def add_group_lags_rolls(df, group_cols, target_col='demand_qty',
                         lags=(1, 3, 7, 14, 21, 28),  # Tambah 3, 21
                         roll_windows=(3, 7, 14, 21, 30)):  # Tambah 3, 21, 30

# Menambah calendar features
def add_calendar_features(df):
    df = df.copy()
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['dayofweek'] = df['date'].dt.dayofweek
    df['weekofyear'] = df['date'].dt.isocalendar().week.astype(int)
    df['is_month_start'] = df['date'].dt.is_month_start.astype(int)
    df['is_month_end'] = df['date'].dt.is_month_end.astype(int)
    
    # TAMBAHAN BARU
    df['quarter'] = df['date'].dt.quarter
    df['is_weekend'] = (df['dayofweek'] >= 5).astype(int)
    df['day_of_year'] = df['date'].dt.dayofyear
    
    return df
```

### 3. **`backend/app/core/utils.py`** - METRICS & UTILITIES
**Untuk mengubah:**
- Threshold zero (0.5 → 0.3)
- Rounding mode
- Metrics evaluasi
- Formula perhitungan

**Contoh perubahan:**
```python
# Mengubah threshold
def eval_with_rounding(y_true, y_pred, thr=0.3):  # dari 0.5 ke 0.3
    x = np.asarray(y_pred, float)
    x = np.where(x < thr, 0, x)
    x = np.floor(x + 0.5)
    return {
        "MAE": mean_absolute_error(y_true, x),
        "RMSE": _rmse(y_true, x),
        "sMAPE%": smape(y_true, x) * 100.0,
        "MAPE%": mape(y_true, x) * 100.0,
    }

# Mengubah rounding mode
def round_series(series, mode='half_up'):
    if mode == 'half_up':
        return np.floor(series + 0.5)
    elif mode == 'round':
        return np.round(series)
    elif mode == 'ceil':
        return np.ceil(series)
    elif mode == 'floor':
        return np.floor(series)
```

---

## 🔄 Langkah-Langkah Update Model

### **Step 1: Backup Model Lama**
```bash
cd /opt/forecast
cp backend/models/best_model.pkl backend/models/best_model_backup.pkl
```

### **Step 2: Edit File yang Diperlukan**
```bash
# Edit file utama
nano backend/app/core/ml_engine.py

# Edit preprocessing
nano backend/app/core/preprocessing.py

# Edit utils
nano backend/app/core/utils.py
```

### **Step 3: Hapus Model Lama**
```bash
# Hapus model lama agar sistem train ulang
rm backend/models/best_model.pkl
```

### **Step 4: Deploy ke Server**
```bash
# Di server
cd /opt/forecast
git pull origin main
docker compose down
docker compose build backend
docker compose up -d
```

### **Step 5: Test Model Baru**
```bash
# Test dengan data sample
curl -X POST http://localhost:9571/api/forecast/submit \
  -F "file=@sample_data.csv" \
  -F "config={\"forecast_horizon\":7}"
```

---

## 🎯 Contoh Update Spesifik

### **Update 1: Mengubah Threshold dari 0.5 ke 0.3**

**File:** `backend/app/core/utils.py`
```python
# Line sekitar 120-130, ubah:
def eval_with_rounding(y_true, y_pred, thr=0.3):  # ubah dari 0.5
```

**File:** `backend/app/core/ml_engine.py`
```python
# Line sekitar 60, ubah:
self.zero_threshold = config.get('zero_threshold', 0.3)  # ubah dari 0.5
```

### **Update 2: Menambah Lag Features**

**File:** `backend/app/core/preprocessing.py`
```python
# Line sekitar 25, ubah:
def add_group_lags_rolls(df, group_cols, target_col='demand_qty',
                         lags=(1, 3, 7, 14, 21, 28),  # tambah 3, 21
                         roll_windows=(3, 7, 14, 21, 30)):  # tambah 3, 21, 30
```

### **Update 3: Mengganti Ridge dengan Random Forest**

**File:** `backend/app/core/ml_engine.py`
```python
# Line sekitar 80-90, ubah:
candidates = {
    "RandomForest": Pipeline([
        ("prep", preprocess_sparse),
        ("reg", RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=self.random_state
        ))
    ])
}
```

---

## ⚠️ Penting untuk Diingat

### **1. Konsistensi dengan Notebook**
- Pastikan perubahan sesuai dengan `model_for_user/forecast11_ridge_only.ipynb`
- Gunakan formula yang sama persis

### **2. Backup Sebelum Update**
- Selalu backup model lama
- Test di environment development dulu

### **3. Update Database Schema (jika perlu)**
- Jika mengubah struktur data, update `backend/app/models.py`
- Jalankan migration jika ada

### **4. Test Thoroughly**
- Test dengan data sample
- Compare hasil dengan model lama
- Monitor performance metrics

---

## 🔍 Debugging Tips

### **Check Model Loading:**
```bash
# Check apakah model berhasil load
docker compose logs backend | grep "Loading existing model"

# Check apakah model baru di-train
docker compose logs backend | grep "Training new model"
```

### **Check Metrics:**
```bash
# Check metrics di database
docker exec forecast_postgres psql -U forecast_user forecast_db -c \
  "SELECT metrics FROM forecast_jobs ORDER BY created_at DESC LIMIT 5;"
```

### **Check Feature Columns:**
```bash
# Check feature yang digunakan
docker compose logs backend | grep "feature_cols"
```

---

## 📊 Monitoring Model Performance

### **Metrics yang Diperhatikan:**
- **MAE** (Mean Absolute Error)
- **RMSE** (Root Mean Square Error)  
- **sMAPE%** (Symmetric Mean Absolute Percentage Error)
- **MAPE%** (Mean Absolute Percentage Error)

### **Threshold Impact:**
- Threshold rendah (0.3) → Lebih banyak prediksi non-zero
- Threshold tinggi (0.7) → Lebih banyak prediksi zero
- Test dengan data real untuk menentukan threshold optimal

---

## 🚀 Quick Update Commands

```bash
# Update threshold ke 0.3
sed -i 's/thr=0\.5/thr=0.3/g' backend/app/core/utils.py
sed -i 's/zero_threshold.*0\.5/zero_threshold.*0.3/g' backend/app/core/ml_engine.py

# Update lag features
sed -i 's/lags=(1,7,14,28)/lags=(1,3,7,14,21,28)/g' backend/app/core/preprocessing.py

# Deploy
docker compose down && docker compose build && docker compose up -d
```

---

**Selalu test perubahan dengan data sample sebelum deploy ke production!** 🎯
