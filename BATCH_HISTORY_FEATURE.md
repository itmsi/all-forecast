# 📊 Batch History & Download Feature

## ✨ Fitur Baru: Batch History dengan Download

History page sekarang mendukung **2 mode**:
1. **Regular Forecast** - History untuk forecast biasa
2. **Batch Forecast** - History untuk batch jobs dengan download

---

## 🎯 Cara Menggunakan

### **1. Akses History Page**

```
http://localhost:9572
→ Click tab "History"
```

### **2. Pilih Mode**

**Tab 1: Regular Forecast**
- Menampilkan regular forecast jobs
- Download button untuk hasil individual

**Tab 2: Batch Forecast** ⭐ BARU!
- Menampilkan batch jobs
- Info partitions (Completed/Skipped/Failed)
- **Download button untuk combined result** ✅

---

## 📊 Batch History Table

### **Columns:**

| Column | Description |
|--------|-------------|
| **Batch ID** | Unique ID untuk batch job |
| **File** | Nama file CSV yang di-upload |
| **Status** | QUEUED / PROCESSING / COMPLETED / FAILED |
| **Partitions** | Breakdown partitions dengan badges |
| **Dibuat** | Waktu batch di-submit |
| **Selesai** | Waktu batch completed |
| **Aksi** | Cancel / Download buttons |

### **Partition Info Badges:**

- 🟢 **Green Badge**: Completed partitions
- 🟡 **Yellow Badge**: Skipped partitions (filtered sites)
- 🔴 **Red Badge**: Failed partitions
- Total: `/13` (example: total 13 partitions)

**Example Display:**
```
🟢 3  🟡 10  / 13
```
- Artinya: 3 completed, 10 skipped, 0 failed, dari total 13 partitions

---

## 📥 Download Batch Result

### **Via History Page:**

1. Buka History page
2. Switch ke tab **"Batch Forecast"**
3. Cari batch job yang status = COMPLETED
4. Click button **"Download"** (biru, dengan icon download)
5. File akan otomatis ter-download

### **File Yang Di-Download:**

```
Filename: batch_forecast_{batch_id}.csv
Format: CSV
Content: Combined forecast dari semua partitions
Columns: date, partnumber, site_code, forecast_qty, forecast_qty_raw, forecast_qty_raw_model
```

### **Via API:**

```bash
# Get batch history
curl http://localhost:9571/api/batch/history

# Download specific batch
curl -O http://localhost:9571/api/batch/download/{batch_id}
```

---

## 🔍 Expandable Row Details

Click row untuk expand dan lihat detail:

```
Batch ID: bb38500c-c40a-41f8-8ade-f31c93ebaea2
Strategy: site
Progress: 100%
Error: (jika ada)
```

---

## ⏭️ Skipped Partitions Feature

### **Apa Itu Skipped?**

Partition di-skip (bukan di-process) jika:
- Config punya `forecast_site_codes` filter
- Site di partition tidak ada dalam filter list
- Partition **TIDAK ERROR**, hanya di-skip karena tidak relevant

### **Contoh:**

```json
Config: {
  "forecast_site_codes": ["IEL-ST-KDI", "Sofifi", "IEL-MU-SFI"]
}

Data punya 13 sites total

Result:
  ✅ 3 partitions COMPLETED (3 filtered sites)
  ⏭️ 10 partitions SKIPPED (sites lain)
  ❌ 0 partitions FAILED
```

### **Display di History:**

```
Partitions: 🟢 3  🟡 10  / 13
```

**Hover tooltip:**
- 🟢 = Completed
- 🟡 = Skipped
- 🔴 = Failed

---

## 🎨 UI Features

### **1. Status Colors**

| Status | Color | Badge |
|--------|-------|-------|
| QUEUED | Gray | Default |
| PROCESSING | Blue | Processing |
| COMPLETED | Green | Success |
| FAILED | Red | Error |
| ROLLED_BACK | Orange | Warning |
| CANCELLED | Gray | Default |

### **2. Action Buttons**

**Cancel Button** (red, untuk PROCESSING):
- Hanya muncul jika status = PROCESSING
- Confirm dialog sebelum cancel
- Batch akan di-stop

**Download Button** (blue primary, untuk COMPLETED):
- Hanya enabled jika status = COMPLETED
- Click untuk download combined result
- Auto-download CSV file

### **3. Pagination**

- Default: 20 items per page
- Sortable by date (newest first)
- Separate pagination untuk Regular vs Batch

---

## 📱 Responsive Design

Table otomatis adjust untuk:
- Desktop: Full table dengan semua kolom
- Tablet: Collapsed columns
- Mobile: Scrollable horizontal

---

## 🔄 Real-time Updates

**Manual Refresh:**
- Click button **"Refresh"** di top-right
- Auto-fetch latest data

**Auto-refresh** (future enhancement):
- Bisa tambahkan auto-refresh setiap 5 detik untuk PROCESSING jobs

---

## 💡 Tips Penggunaan

### **1. Monitor Running Batch**

```
1. Submit batch via Dashboard
2. Switch ke History page → Tab "Batch Forecast"
3. Click Refresh setiap beberapa detik
4. Lihat progress di column "Partitions"
5. Tunggu status jadi COMPLETED
6. Click Download
```

### **2. Cek Skipped Partitions**

```
1. Lihat yellow badge (🟡) di column Partitions
2. Hover untuk tooltip "Skipped"
3. Click row untuk expand detail
4. Lihat filter sites di config
```

### **3. Troubleshoot Failed Batch**

```
1. Cari batch dengan status FAILED
2. Click row untuk expand
3. Baca error message
4. Check failed_partitions (red badge 🔴)
```

---

## 🚀 Workflow Lengkap

### **End-to-End Batch Forecast:**

```
1. Dashboard → Upload CSV file
2. Set config (forecast_days, site filter, dll)
3. Submit Batch
4. History → Tab "Batch Forecast"
5. Monitor progress (refresh manual)
6. Wait for COMPLETED
7. Click Download
8. ✅ Done!
```

---

## 📋 API Reference

### **Get Batch History**

```http
GET /api/batch/history?page=1&page_size=20

Response:
{
  "total": 13,
  "page": 1,
  "page_size": 20,
  "jobs": [
    {
      "batch_job_id": 11,
      "batch_id": "bb38500c...",
      "original_filename": "alldemand_augjul.csv",
      "status": "COMPLETED",
      "progress": 100,
      "partition_strategy": "site",
      "total_partitions": 13,
      "completed_partitions": 3,
      "skipped_partitions": 10,
      "failed_partitions": 0,
      "created_at": "2025-10-15T02:11:57...",
      "completed_at": "2025-10-15T02:12:34...",
      "combined_output": "outputs/bb38500c.../combined_forecast.csv"
    }
  ]
}
```

### **Download Batch Result**

```http
GET /api/batch/download/{batch_id}

Response:
  Content-Type: text/csv
  Content-Disposition: attachment; filename="batch_forecast_{batch_id}.csv"
  
  File berisi combined forecast dari semua completed partitions
```

### **Cancel Batch Job**

```http
POST /api/batch/cancel/{batch_id}

Response:
{
  "message": "Batch {batch_id} cancelled",
  "batch_id": "...",
  "status": "CANCELLED"
}
```

---

## 🎯 Key Features Summary

### ✅ **Yang Sudah Ditambahkan:**

1. **Tab System** - Separate Regular & Batch history
2. **Batch Table** - Columns khusus untuk batch jobs
3. **Partition Badges** - Visual indicator untuk completed/skipped/failed
4. **Download Button** - Download combined batch result
5. **Cancel Button** - Cancel running batch
6. **Expandable Rows** - Show detail batch info
7. **Backward Compatible** - Support old records tanpa skipped_partitions

### ✅ **User Experience:**

- 🎨 Beautiful UI dengan badges dan colors
- 📊 Clear partition status visualization
- 📥 Easy download dengan 1 click
- ⚠️ Clear error messages
- 🔄 Refresh button untuk update manual
- 💡 Tooltips untuk guidance

---

## 🧪 Testing Checklist

- [x] Submit batch forecast
- [x] View di History → Batch tab
- [x] Lihat partition badges (completed/skipped/failed)
- [x] Click expand row untuk detail
- [x] Click Download button
- [x] Verify file ter-download
- [x] Test Cancel button untuk running batch
- [x] Test pagination
- [x] Test refresh button

---

## 📝 Notes

### **Skipped Partitions:**

Old batch jobs (sebelum fix) akan show `skipped_partitions: 0` karena:
- Database column baru ditambahkan
- Backward compatibility: `getattr(self, 'skipped_partitions', 0)`
- Batch jobs baru akan track skipped correctly

### **Download Behavior:**

- Button **disabled** jika status != COMPLETED
- Download langsung trigger browser download
- Filename format: `batch_forecast_{batch_id}_{date}.csv`
- File location di backend: `outputs/{batch_id}/combined_forecast.csv`

---

## 🚀 Future Enhancements (Optional)

1. **Auto-refresh** untuk PROCESSING batches
2. **Progress bar** di table
3. **Filter by status** untuk batch tab
4. **Search by filename**
5. **Bulk delete** untuk multiple batches
6. **Export batch summary** to Excel

---

## ✅ Status

**Feature: Batch History & Download** → ✅ **COMPLETED & PRODUCTION READY!**

Users can now:
- ✅ View batch history
- ✅ Download batch results dengan 1 click
- ✅ Monitor partition status (completed/skipped/failed)
- ✅ Cancel running batches
- ✅ Track all batch jobs dengan clear UI


