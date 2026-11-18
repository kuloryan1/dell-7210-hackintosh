# Dell Latitude 7210 2-in-1 Hackintosh (macOS Sonoma & Sequoia)

[![OpenCore](https://img.shields.io/badge/OpenCore-0.9.x+-blue.svg)](https://github.com/acidanthera/OpenCorePkg)
[![macOS Sonoma](https://img.shields.io/badge/macOS-Sonoma%2014.x-green.svg)](https://www.apple.com/macos/sonoma/)
[![macOS Sequoia](https://img.shields.io/badge/macOS-Sequoia%2015.x-success.svg)](https://www.apple.com/macos/sequoia/)
[![Hardware](https://img.shields.io/badge/Intel-Comet%20Lake--U-orange.svg)](https://ark.intel.com/)

Repositori OpenCore EFI, panduan instalasi pemula, dan data pengujian lengkap untuk **Dell Latitude 7210 2-in-1 Tablet**.

Repositori ini disusun secara transparan dan jujur: **semua fitur yang bekerja, solusi kendala, maupun batasan hardware dipaparkan apa adanya tanpa ditutupi atau menyesatkan**.

---

## 📋 Spesifikasi Hardware Unit Uji

| Komponen | Spesifikasi | Status di macOS |
| :--- | :--- | :--- |
| **Model** | Dell Latitude 7210 2-in-1 (Tablet Form Factor) | ✅ Teridentifikasi sebagai `MacBookPro16,3` |
| **Prosesor (CPU)** | Intel Core i7-10610U (Comet Lake-U, 4C/8T, 15W TDP) | ✅ SpeedShift / HWP & Turbo Boost aktif |
| **Grafis (iGPU)** | Intel UHD Graphics 620 (`0x3E9B` / platform `0x3E9B0000`) | ✅ Metal Support, VRAM 2048 MB, Akselerasi Video |
| **Layar** | 12.3" IPS 1920×1280 (Rasio 3:2) | ✅ Kecerahan layar (slider & tombol Fn) lancar |
| **Memori (RAM)** | 16 GB LPDDR3 2133 MHz (Soldered) | ✅ Terbaca native |
| **Penyimpanan** | NVMe KIOXIA 256 GB (PCIe Gen3 x4) | ✅ APFS lancar via `NVMeFix.kext` + TRIM |
| **Audio Codec** | Realtek ALC295 (Layout ID: 33) | ✅ Speaker stereo & Mic internal jernih |
| **Jaringan Nirkabel** | Intel Wi-Fi AX201 & Intel Bluetooth | 🟡 Bekerja (Sonoma: Native Airport; Sequoia: itlwm) |
| **Keyboard & Touchpad** | Dell Detachable Folio Cover (`044E:1218`) | ✅ Keyboard, Fn keys, & Alps Touchpad aktif |
| **Layar Sentuh** | Intel I2C Multitouch & Stylus Pen | 🟡 Sentuhan dasar & Stylus hover/klik aktif |
| **Kamera** | Webcam Depan UVC USB | ✅ Bekerja normal di FaceTime / Zoom |
| **MicroSD Reader** | Realtek Card Reader (PCIe) | 🔴 Tidak stabil / Sering timeout (Jangan gunakan) |
| **Fingerprint** | Sensor Sidik Jari Goodix | 🔴 Tidak didukung (Tidak ada driver macOS) |

---

## 🚦 Status Matriks Fitur (Transparan 100%)

> [!NOTE]
> Untuk penjelasan teknis mendalam dan bukti pengujian masing-masing komponen, baca dokumen [docs/STATUS_DAN_BATASAN.md](docs/STATUS_DAN_BATASAN.md).

### 🟢 Bekerja Sempurna:
- [x] Booting UEFI OpenCore cepat dan stabil
- [x] Akselerasi grafis penuh (Metal 3, decoding H.264 & HEVC)
- [x] Resolusi native 1920×1280 rasio 3:2 dengan kontrol kecerahan layar
- [x] Audio speaker stereo, mikrofon internal, dan headphone 3.5mm
- [x] Keyboard folio detachable dan AlpsHID touchpad
- [x] Port USB Type-C (Thunderbolt 3) dan port USB Type-A 3.0
- [x] Pemantauan baterai akurat (persentase, status charger, discharge rate)
- [x] Sensor suhu prosesor dan kipas pendingin Dell EC
- [x] Kamera depan UVC (FaceTime, Photobooth, Web Browser)
- [x] Tombol fisik tablet (Volume +/- dan Power Button) via `YogaSMCAlter-L7210`

### 🟡 Bekerja dengan Catatan / Workaround:
- [x] **Wi-Fi & Bluetooth**:
  - Di Sonoma: Menggunakan `AirportItlwm.kext` (menu native).
  - Di Sequoia: Disarankan `itlwm.kext` + `HeliPort.app` guna menghindari crash driver.
  - AirDrop: Wajib disetel `DiscoverableMode = Off` untuk mencegah banjir CPU `logd` (lihat [docs/PENANGANAN_LOG_DAN_AIRDROP.md](docs/PENANGANAN_LOG_DAN_AIRDROP.md)).
- [x] **Touchscreen & Pen**:
  - Touchscreen sentuh navigasi dasar bekerja lancar.
  - Stylus pen mendeteksi hover dan klik, namun tekanan tidak sehalus Apple Pencil.
- [x] **Manajemen Tidur (Sleep/Wake)**:
  - Tidur otomatis bekerja, namun wajib disetel `lidwake 0` agar magnet cover folio tidak membangunkan laptop di dalam tas (lihat `scripts/optimize-sleep.sh`).

### 🔴 Tidak Bekerja (Batasan Hardware):
- [ ] **Sensor Sidik Jari (Fingerprint Reader)**: Tidak didukung di macOS (tidak ada driver untuk Touch ID pihak ketiga).
- [ ] **Slot MicroSD Reader**: Driver `RealtekCardReader.kext` mendeteksi hardware tetapi inisialisasi media sering `CMD8 timeout` / `ACMD41 NOT READY`. **Tidak disarankan untuk transfer data penting**.
- [ ] **Kamera Belakang & Windows Hello IR**: Sensor biometrik inframerah dan sensor IPU4 tidak didukung macOS.
- [ ] **Rotasi Layar Otomatis**: Sensor akselerometer tablet tidak terintegrasi ke sistem rotasi macOS.

---

## ⚠️ PERINGATAN KRITIS: Throttling & Bahaya Panic

> [!CAUTION]
> ### 1. Bahaya Kernel Panic: MSR 0x772 & 0x773
> **JANGAN PERNAH** mencoba membaca atau menulis ke register MSR `0x772` atau `0x773` pada prosesor Comet Lake-U!
> Register ini tidak didukung oleh hardware dan akan langsung memicu **General Protection Exception (#GP Type 13) Kernel Panic**. Selalu gunakan wrapper pengaman di [`scripts/voltageshift`](scripts/voltageshift).

> [!WARNING]
> ### 2. Throttling Ekstrem Dell: BD PROCHOT (400 MHz)
> Embedded Controller Dell dapat mengunci kecepatan prosesor di **0.4 GHz (400 MHz)** dan membatasi konsumsi daya ke 4 Watt saat terjadi anomali charger atau suhu.
> Repositori ini menyertakan perbaikan instan untuk mematikan bit BD PROCHOT (MSR `0x1FC`) serta membuka batas daya ke **55 Watt** (MSR `0x610`). Detail lengkap: [docs/OPTIMASI_MSR_DAN_PERFORMA.md](docs/OPTIMASI_MSR_DAN_PERFORMA.md).

---

## 📖 Panduan Dokumentasi Lengkap

Silakan pelajari panduan terperinci di bawah ini:

1. 📘 **[Panduan Lengkap Instalasi untuk Pemula](docs/PANDUAN_PEMULA_INSTALL.md)**:
   - Setting BIOS Dell Latitude 7210.
   - Cara membuat bootable USB macOS.
   - Langkah memasang EFI dan proses format disk APFS.
2. 🔑 **[Wajib: Generate Serial Number Baru](docs/PANDUAN_PEMULA_INSTALL.md#5-wajib-generate-serial-number-smbios-baru)**:
   - Wajib generate `MacBookPro16,3` via GenSMBIOS sebelum login ke Apple ID / iCloud!
3. ⚡ **[Panduan Optimasi MSR, Power Limit, & Pencegahan Panic](docs/OPTIMASI_MSR_DAN_PERFORMA.md)**:
   - Pelepasan kunci 400 MHz, PL1/PL2 55W, dan filter pengaman kernel panic.
4. 🩺 **[Solusi Lonjakan CPU logd (80%) & Loop AirDrop Intel](docs/PENANGANAN_LOG_DAN_AIRDROP.md)**:
   - Cara membersihkan `/var/db/diagnostics` dan mematikan AirDrop discoverability loop.
5. 🍏 **[Panduan Update ke macOS Sequoia (15.x)](docs/UPDATE_MACOS_SEQUOIA.md)**:
   - Langkah aman update OS tanpa bootloop dan panduan konfigurasi HeliPort.
6. 🔬 **[Dokumentasi Hasil Uji & Riwayat Log Testing](testing/README.md)**:
   - Berisi 45 file log OpenCore asli, dump ACPI/SysReport asli pabrik, dan script audit Linux.

---

## 🚀 Panduan Singkat Pasca Instalasi (Post-Install)

Setelah Anda berhasil masuk ke desktop macOS:

1. Buka aplikasi **Terminal**.
2. Masuk ke folder repositori ini dan jalankan script installer otomatis:
   ```bash
   # Pasang seluruh skrip optimasi & background guardian service:
   bash scripts/install-launchagents.sh

   # Terapkan konfigurasi manajemen daya hemat baterai:
   bash scripts/optimize-sleep.sh

   # Aktifkan TRIM SSD internal:
   sudo trimforce enable
   ```
3. Restart laptop Anda. Sistem sekarang berjalan dengan perlindungan throttling otomatis dan hemat baterai!

---

## 🗂️ Struktur Repositori

```
Dell 7210/
├── EFI/                    # Folder EFI utama siap pakai (OpenCore 0.9.x+)
│   ├── BOOT/               # Boot loader BOOTx64.efi
│   └── OC/                 # OpenCore core, ACPI, Kexts, Drivers, config.plist
├── docs/                   # Panduan teknis lengkap & transparan
│   ├── PANDUAN_PEMULA_INSTALL.md     # Panduan langkah demi langkah pemula
│   ├── STATUS_DAN_BATASAN.md         # Status 100% jujur seluruh hardware
│   ├── OPTIMASI_MSR_DAN_PERFORMA.md  # Bedah BD PROCHOT 400MHz & bahaya MSR 0x772
│   ├── PENANGANAN_LOG_DAN_AIRDROP.md # Solusi logd 80% & loop AirDrop Intel
│   └── UPDATE_MACOS_SEQUOIA.md       # Panduan update aman ke macOS Sequoia
├── scripts/                # Skrip optimasi & proteksi sistem
│   ├── install-launchagents.sh       # Installer otomatis untuk semua user
│   ├── dell-logguard.sh              # Guardian: PL 55W, PROCHOT off, AirDrop fix
│   ├── optimize-sleep.sh             # Konfigurasi pmset deep sleep
│   ├── ram-warmup.sh                 # Pre-warm buffer cache & SQLite maintenance
│   └── voltageshift                  # Safety wrapper penangkal Kernel Panic MSR
├── launchagents/           # Layanan otomatis launchd macOS
│   ├── com.dell7210.logguard.plist
│   ├── com.dell7210.jackfix.plist
│   └── com.dell7210.ramwarmup.plist
├── testing/                # Data pengujian & bukti otentik
│   ├── SysReport/          # ACPI DSDT/SSDT, CPUInfo, PCIInfo bawaan mesin
│   ├── audit/              # Hasil audit komparasi hardware Linux & Windows
│   ├── opencore-logs/      # 45 file log boot OpenCore (debugging riil)
│   ├── config-history/     # Riwayat revisi config.plist selama testing
│   └── acpi-source/        # Source DSL (SSDT-PNLF.dsl)
└── extra/                  # Konfigurasi tambahan (Firefox user.js, dll)
```

---

## 🤝 Ucapan Terima Kasih & Referensi

- [Acidanthera](https://github.com/acidanthera) untuk OpenCore, Lilu, WhateverGreen, VirtualSMC, AppleALC, VoodooPS2.
- [OpenIntelWireless](https://github.com/OpenIntelWireless) untuk AirportItlwm, itlwm, dan IntelBluetoothFirmware.
- [VoodooI2C](https://github.com/VoodooI2C/VoodooI2C) & [AlpsHID](https://github.com/blankmac/AlpsHID) untuk dukungan Touchscreen dan Touchpad.
- [zhen-zen](https://github.com/zhen-zen/YogaSMC) untuk YogaSMC.
- [sicreative](https://github.com/sicreative/VoltageShift) untuk VoltageShift.
- [0xFireWolf](https://github.com/0xFireWolf/RealtekCardReader) untuk RealtekCardReader.
- [Dortania OpenCore Guide](https://dortania.github.io/OpenCore-Install-Guide/) sebagai panduan referensi utama.
