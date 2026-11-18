# Penanganan Beban CPU Tinggi (logd 80%) & Loop AirDrop Intel

Dokumen ini memaparkan akar masalah lonjakan beban proses latar belakang `logd` pada macOS yang sering menyebabkan laptop terasa hangat, baterai cepat boros, dan ruang penyimpanan SSD tersita tanpa disadari.

---

## 🔍 1. Akar Masalah

Pada laptop Hackintosh yang menggunakan kartu nirkabel **Intel (AX201 / AC Series)**, sistem operasi macOS (terutama versi Sonoma dan Sequoia) mencoba menjalankan layanan pencarian perangkat Apple di sekitar melalui protokol **Bluetooth Low Energy (BLE)** untuk fitur AirDrop, Find My, dan Handoff.

Karena chipset Intel tidak memiliki kompatibilitas firmware Apple native yang 100% sempurna:
1. Proses **`sharingd`**, **`bluetoothd`**, dan **`airportd`** masuk ke dalam siklus loop tanpa henti (mencapai ~73 pesan log per detik).
2. Setiap pesan loop dicatat ke dalam subsistem logging macOS oleh daemon **`logd`**.
3. Akibatnya:
   - Penggunaan CPU oleh **`logd`** melonjak hingga **60% – 80%**.
   - Database log di `/var/db/diagnostics/` membengkak dari ukuran normal beberapa Megabyte menjadi **1.7 GB+**.
   - Laptop menjadi panas dan kipas pendingin terus berputar kencang.

---

## 🛠️ 2. Solusi & Langkah Penanganan

### Langkah 1: Mematikan Mode Visibilitas AirDrop
Karena kartu Intel tidak dapat menerima transfer AirDrop native secara stabil, matikan mode deteksi AirDrop agar `sharingd` tidak terus memindai:
```bash
defaults write com.apple.sharingd DiscoverableMode -string "Off"
killall sharingd
```

### Langkah 2: Membersihkan Tumpukan Database Log yang Membengkak
Jalankan pembersihan log store secara aman melalui terminal:
```bash
sudo log erase --all
sudo rm -rf /var/db/diagnostics/*
sudo rm -rf /var/db/uuidtext/*
```
*Tindakan ini akan mengembalikan ruang disk hingga bergiga-giga byte dan mengembalikan beban `logd` ke level 0.0% – 0.1% CPU.*

### Langkah 3: Otomasi Pengawasan via `dell-logguard`
Skrip [`scripts/dell-logguard.sh`](file:///Users/kuloryan/Documents/Github/Dell%207210/scripts/dell-logguard.sh) secara proaktif memeriksa apakah `logd` mengalami lonjakan beban abnormal di atas 40% CPU. Jika terdeteksi, daemon `logd` akan di-refresh (`killall -HUP logd`) secara otomatis tanpa mengganggu aplikasi yang sedang dibuka.

---

## 📊 3. Hasil Pengujian Sebelum vs Sesudah

| Parameter | Sebelum Penanganan | Sesudah Optimasi | Status |
| :--- | :--- | :--- | :--- |
| **Beban CPU `logd`** | 60% – 80% CPU | **0.0% – 0.1% CPU** | ✅ Sempurna |
| **Laju Pesan Sistem** | 73.1 pesan/detik | **0.33 pesan/detik** | ✅ Sangat Hening |
| **Ukuran Log Store** | 1.74 GB (Bengkak) | **< 66 MB** | ✅ Ramping |
| **Suhu CPU Saat Idle** | ~65°C – 70°C | **~42°C – 48°C** | ✅ Sejuk & Hening |
