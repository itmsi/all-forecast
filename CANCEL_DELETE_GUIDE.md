# 🛑 Cancel & Force Delete Guide

## 🎯 Fitur Anti-Stuck untuk Production

### **Problem yang Diselesaikan:**
- ❌ Job stuck tidak bisa dihentikan
- ❌ Server resource terpakai terus
- ❌ Tidak bisa re-submit job baru
- ❌ Harus restart container

### **Solution:**
- ✅ Cancel button untuk stop job
- ✅ Force delete untuk cleanup
- ✅ Instant termination (1-2 detik)
- ✅ Server resources freed

---

## 🚀 Cara Menggunakan

### **1. Stop Job yang Sedang Running**

#### **Dari Dashboard:**
```
Job Status: PROCESSING
         ↓
Button "Stop Job" (red) muncul
         ↓
Click "Stop Job"
         ↓
Confirmation: "Job akan dihentikan..."
         ↓
Click "Ya, Stop"
         ↓
Job terminated dalam 1-2 detik
         ↓
Status: CANCELLED ✅
```

**Kapan Pakai:**
- Job stuck >5 menit tanpa progress
- Upload wrong file/config
- Need to re-submit dengan parameter beda

---

### **2. Delete Job dari History**

#### **Delete Normal (COMPLETED/FAILED jobs):**
```
History Page → Find job
         ↓
Button "Hapus" (enabled untuk COMPLETED/FAILED)
         ↓
Click "Hapus"
         ↓
Confirmation
         ↓
Job + files deleted ✅
```

#### **Force Delete (PROCESSING jobs):**
```
History Page → Find stuck job
         ↓
Button "Force Delete" (red)
         ↓
Click "Force Delete"
         ↓
Warning: "Job masih running! Akan di-STOP..."
         ↓
Click "Ya, Force Delete"
         ↓
Job terminated + deleted dalam 1-2 detik ✅
```

---

## ⚠️ Kapan Harus Stop/Cancel Job?

### **Indikator Job Stuck:**

1. **Progress Freeze** (>3 menit)
   ```
   Progress: 35%... 35%... 35%... (tidak berubah)
   Action: Stop Job ✅
   ```

2. **Waktu Abnormal** (>5 menit dengan filter site)
   ```
   Expected: 2-3 menit
   Actual: 10+ menit
   Action: Stop Job ✅
   ```

3. **No Log Activity** (check via terminal)
   ```bash
   docker-compose logs -f celery_worker
   # Jika tidak ada log baru >2 menit
   Action: Stop Job ✅
   ```

---

## 🔍 Visual Guide - Button Locations

### **Dashboard (Saat PROCESSING):**
```
┌─────────────────────────────────────────────────┐
│  [🚀 Jalankan Forecast] [🛑 Stop Job] [Reset]   │
│      (disabled)            (red)                │
└─────────────────────────────────────────────────┘
```

### **History (Different Status):**
```
Status: PROCESSING
Actions: [🛑 Stop] [📥 Download (disabled)] [🗑️ Force Delete]

Status: COMPLETED
Actions: [📥 Download] [🗑️ Hapus]

Status: FAILED/CANCELLED
Actions: [📥 Download (disabled)] [🗑️ Hapus]
```

---

## 🧪 Testing Scenarios

### **Test 1: Cancel Normal Job**
```bash
1. Upload file dengan Site = IEL-ST-KDI
2. Submit forecast
3. Tunggu 30 detik (progress ~15%)
4. Click "Stop Job"
5. Verify: Status → CANCELLED
6. Verify: Progress bar stopped
7. Verify: Server resources freed
```

### **Test 2: Force Delete Stuck Job**
```bash
1. Go to History page
2. Find job dengan status PROCESSING
3. Click "Force Delete"
4. Confirm action
5. Verify: Job hilang dari list
6. Verify: Files deleted
```

### **Test 3: Regular Delete Completed Job**
```bash
1. Complete a forecast
2. Download hasil CSV
3. Go to History
4. Click "Hapus"
5. Verify: Job deleted
```

---

## 📊 Expected Behavior

### **After Cancel:**
```
Database:
├─ Job status → CANCELLED
├─ error_message → "Cancelled by user"
├─ completed_at → timestamp
└─ progress → 0

Celery:
├─ Task terminated
├─ Worker freed
└─ Ready for new jobs

Files:
├─ Upload file → kept (for audit)
└─ Output file → not created (incomplete)
```

### **After Force Delete:**
```
Database:
└─ Job removed completely

Celery:
└─ Task terminated (if running)

Files:
├─ Upload file → deleted
└─ Output file → deleted (if exists)
```

---

## 🚨 Important Notes

### **Cancel vs Force Delete:**

| Action | Cancel | Force Delete |
|--------|--------|--------------|
| Job Status After | CANCELLED (kept in DB) | Deleted (removed from DB) |
| Files | Kept | Deleted |
| Can Undo? | No | No |
| Use When | Want to stop & keep record | Want to cleanup completely |

### **Recommendations:**

✅ **Use Cancel** if:
- Want audit trail (job history)
- Want to analyze why stuck
- Testing/debugging

✅ **Use Force Delete** if:
- Cleanup stuck jobs
- Free disk space
- Remove wrong uploads

---

## 🎉 Benefits

1. **Server Protection**
   - No more resource hogging
   - Can handle stuck jobs
   - Automatic cleanup

2. **User Control**
   - Stop anytime
   - Re-submit easily
   - No waiting hours

3. **Production Ready**
   - Confirmation dialogs
   - Error handling
   - Clean termination

---

**System is now PRODUCTION READY with full job control!** 🚀
