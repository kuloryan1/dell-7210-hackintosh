# Status Hardware & Batasan (Transparan & Tanpa Ditutupi)

Dokumen ini memuat status kerja seluruh komponen perangkat keras pada **Dell Latitude 7210 2-in-1** saat menjalankan macOS (Sonoma 14.x & Sequoia 15.x). Semua informasi ditulis berdasarkan hasil audit perangkat keras, log OpenCore, dan pengujian riil tanpa ada yang disembunyikan.

---

## 🟢 1. Bekerja Sempurna (Fully Working)

| Komponen | Detail Teknis | Catatan |
| :--- | :--- | :--- |
| **Bootloader** | OpenCore (0.9.x+) | Boot stabil, GUI picker bekerja, SIP & NVRAM berfungsi. |
| **Prosesor (CPU)** | Intel Core i7-10610U (Comet Lake-U, 4 Core / 8 Thread) | SpeedShift / HWP aktif, manajemen daya native via `CPUFriend` & `CPUFriendDataProvider`. |
| **Akselerasi Grafis (iGPU)** | Intel UHD Graphics 620 (`0x3E9B`) | Full Metal Support, akselerasi video Hardware (HEVC / H.264), VRAM 2048 MB via WhateverGreen. |
| **Layar Bawaan** | 12.3" IPS 1920×1280 (3:2) | Kecerahan layar (brightness slider & tombol Fn) bekerja halus via `BrightnessKeys` & patch PNLF. |
| **Audio Speaker & Mic** | Realtek ALC295 (Layout ID: 33) | Speaker stereo kiri/kanan jernih, mikrofon internal bekerja normal via `AppleALC.kext`. |
| **Keyboard Folio** | Dell Detachable Keyboard | Tombol ketik, tombol fungsi (Fn), backlight keyboard bekerja via `VoodooPS2Controller.kext`. |
| **Touchpad Folio** | AlpsHID (`044E:1218`) | Pointer presisi, klik kiri/kanan, scrolling bekerja via `AlpsHID.kext`. |
| **Status Baterai** | Dual Battery / Smart Battery ACPI | Persentase baterai, sisa waktu, dan status charging akurat via `SMCBatteryManager.kext`. |
| **Port USB Type-C & Type-A** | USB 3.1 Gen 2 & USB 3.0 | Seluruh port terpetakan rapi (15 port limit terjaga) via `UTBMap-L7210.kext` & `USBToolBox.kext`. |
| **Webcam Depan** | UVC USB Camera | Terdeteksi native oleh macOS untuk FaceTime, Zoom, Google Meet. |
| **Sensor Suhu & Kipas** | Dell Embedded Controller Sensor | Terbaca di aplikasi monitoring via `SMCDellSensors.kext` & `SMCProcessor.kext`. |

---

## 🟡 2. Bekerja Sebagian / Memerlukan Catatan Khusus (Partial / Workaround)

### A. Wi-Fi & Bluetooth (Intel AX201 / AC)
- **macOS Sonoma (14.x)**: Bekerja native di menu Wi-Fi macOS menggunakan `AirportItlwm.kext`.
- **macOS Sequoia (15.x)**: Driver `AirportItlwm` pada Sequoia sering memicu loop scanning Bluetooth Low Energy (BLE) yang menyebabkan CPU `logd` melonjak hingga 80% dan memicu panas.
  - *Rekomendasi Sequoia*: Gunakan driver `itlwm.kext` + aplikasi **HeliPort.app** untuk koneksi Wi-Fi yang stabil dan dingin.
- **AirDrop & Continuity**: Fitur AirDrop Apple membutuhkan kartu Wi-Fi Broadcom native Apple. Kartu Intel **tidak mendukung AirDrop native secara sempurna**. Pastikan AirDrop disetel ke `DiscoverableMode = Off` untuk mencegah banjir pesan log di macOS.

### B. Touchscreen & Stylus Pen
- **Touchscreen**: Bekerja via `VoodooI2C.kext` + `VoodooI2CHID.kext` untuk navigasi sentuh dasar (tap, drag). Tidak mendukung gesture multi-touch kompleks khas iPadOS.
- **Stylus Pen (Dell Active Pen)**: Terdeteksi dengan fungsi hover dan klik tombol. Tingkat sensitivitas tekanan (*pressure sensitivity*) hanya dasar dan tidak sehalus Apple Pencil / tablet grafis Wacom profesional.

### C. Tombol Fisik Tablet (Power & Volume)
- Tombol volume samping dan tombol power tablet di-routing melalui ACPI Intel HID (`INT33D5`) menggunakan kext modifikasi `YogaSMCAlter-L7210.kext`.
- Tombol power fisik memerlukan pengaturan:
  ```bash
  defaults write com.apple.loginwindow PowerButtonSleepsSystem -bool true
  ```
  agar penekanan singkat tombol power langsung menidurkan layar.

### D. Jack Headphone (3.5mm)
- Audio headphone keluar dengan jernih. Namun, pada saat cabut-pasang jack tertentu, deteksi kombo mikrofon headset memerlukan background watcher / JackFix daemon agar jalur audio beralih otomatis tanpa noise statis.

### E. Manajemen Tidur (Sleep / Wake)
- Sleep S0ix / Modern Standby dapat berfungsi normal jika tidak ada peripheral eksternal yang membangunkan sistem secara acak.
- **Masalah "Backpack Wake"**: Cover keyboard magnetik atau mouse Bluetooth dapat membangunkan laptop di dalam tas ransel. Wajib menerapkan:
  ```bash
  sudo pmset -b lidwake 0 displaysleep 5 sleep 15 disksleep 10
  ```
  *(Disediakan di `scripts/optimize-sleep.sh`)*.

---

## 🔴 3. Tidak Bekerja / Pembatasan Hardware (Not Working / Limitations)

| Fitur | Status | Alasan Teknis |
| :--- | :--- | :--- |
| **Fingerprint Reader (Sensor Sidik Jari)** | **TIDAK BEKERJA** | macOS hanya mendukung Touch ID resmi Apple melalui chip Secure Enclave (T2 / Apple Silicon). Sensor sidik jari PC (Goodix/Synaptics) **mustahil** difungsikan di Hackintosh mana pun. |
| **Slot MicroSD Reader (Realtek)** | **TIDAK STABIL / SERING GAGAL** | Driver `RealtekCardReader.kext` (v0.9.7) mendeteksi kehadiran card reader, namun saat inisialisasi kartu SD sering terjadi `CMD8 timeout` dan `ACMD41 NOT READY`. Kartu sering kali tidak muncul di Finder. **Jangan gunakan untuk menyimpan data penting.** |
| **Kamera Belakang (World-Facing Camera)** | **DIDUKUNG SECARA HARDWARE (UVC 8M)** | Menggunakan sensor USB UVC Realtek Integrated_Webcam_8M (`0bda:565e`) pada port internal SS02. Mendukung resolusi hingga 3264×2448. Pada macOS, kamera belakang dapat dipilih melalui aplikasi pihak ketiga (Zoom, Google Meet, OBS) atau QuickTime Player (pilih kamera pada dropdown). Pastikan `Camera2` aktif di BIOS. |
| **Slot Kartu SIM & Modem WWAN LTE** | **BEKERJA VIA PPP (TERVERIFIKASI)** | Menggunakan modem Dell DW5821e-eSIM Qualcomm Snapdragon X20 (`413c:81e0`). Kartu SIM terdeteksi (`CPIN: READY`), terdaftar jaringan LTE, dan koneksi IP diperoleh via `pppd` menggunakan aplikasi jembatan `Modem Smartfren.app` / `SAMBUNG-SMARTFREN.command`. |
| **Windows Hello IR Camera** | **TIDAK BEKERJA** | Sensor inframerah biometrik tidak didukung oleh macOS. |
| **Sensor Rotasi Otomatis (Auto-Rotate)** | **TIDAK BEKERJA** | Sensor akselerometer/giroskop IIO pada Dell tidak diintegrasikan oleh Apple ke rotasi layar macOS (hanya bisa rotasi manual via System Settings > Displays). |
| **Apple Pay via Touch ID** | **TIDAK BEKERJA** | Memerlukan Secure Enclave Apple. |

---

## ⚠️ 4. Peringatan Penting Soal Throttling & Kernel Panic

### 1. Masalah Throttling Dell (BD PROCHOT 400 MHz)
Dell Latitude 7210 memiliki mekanisme proteksi suhu Embedded Controller (EC) yang sangat agresif. Jika mendeteksi anomali charger USB-PD atau suhu mendadak, EC akan mengunci prosesor di **0.4 GHz (400 MHz)** dan membatasi konsumsi daya CPU ke **~4 Watt**, membuat sistem terasa sangat lambat (lag parah).
- **Solusi**: Bit 0 pada MSR `0x1FC` harus dinonaktifkan (`0x0024005E`) menggunakan skrip `scripts/dell-logguard.sh`.

### 2. PERINGATAN BAHAYA: MSR 0x772 & 0x773
> [!CAUTION]
> **JANGAN PERNAH** memanggil register MSR `0x772` atau `0x773` di prosesor Intel Comet Lake-U!
> Pemanggilan register ini akan langsung memicu **Kernel Panic (#GP Type 13 / General Protection Fault)** yang membuat macOS langsung restart seketika. Selalu gunakan skrip wrapper `scripts/voltageshift` yang sudah dilengkapi filter pengaman.
