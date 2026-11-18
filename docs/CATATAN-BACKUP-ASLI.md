# Hackintosh Dell Latitude 7210 — Backup & Restore Guide

> Backup dibuat: November 2026  
> macOS: Sequoia 15.8.2 via OpenCore

---

## 📋 Spesifikasi Hardware

| Komponen | Spesifikasi |
|----------|-------------|
| **Model** | Dell Latitude 7210 2-in-1 (Tablet form factor) |
| **CPU** | Intel Core i7-10610U (Comet Lake-U, 4C/8T, 15W TDP) |
| **Clock** | Base 1.8 GHz / Boost 4.9 GHz |
| **RAM** | 16 GB LPDDR3 |
| **Storage** | NVMe KIOXIA KBG40ZNS256G 256GB (PCIe Gen3 x4) |
| **GPU** | Intel UHD Graphics 620 (Device ID: 0x3E9B) |
| **Display** | 1920×1280 @ 60Hz (rasio 3:2) |
| **WiFi/BT** | Intel (AX201 atau setara) |

## 🍎 macOS / OpenCore

| Item | Nilai |
|------|-------|
| **macOS** | Sequoia 15.8.2 |
| **Bootloader** | OpenCore (versi terbaru saat backup) |
| **SMBIOS** | MacBookPro16,3 |
| **GPU Platform-ID** | 0x3E9B0000 |

---

## 📦 Daftar Kext (EFI/OC/Kexts/)

| Kext | Versi | Fungsi |
|------|-------|--------|
| Lilu | 1.7.2 | Foundation patch |
| WhateverGreen | 1.7.1 | GPU iGPU fix |
| CPUFriend | 1.3.0 | CPU power management |
| CPUFriendDataProvider | custom | Data tuning CPUFriend |
| VirtualSMC | 1.3.8 | SMC emulasi |
| SMCBatteryManager | 1.3.8 | Status baterai |
| AppleALC | latest | Audio codec |
| AirportItlwm | Sequoia | Intel WiFi |
| IntelBluetoothFirmware | latest | Bluetooth Intel |
| BlueToolFixup | latest | BT macOS 12+ fix |
| VoodooI2C | latest | Touchscreen/touchpad I2C |
| VoodooPS2Controller | latest | Keyboard PS2 |
| BrightnessKeys | latest | Fn + brightness keys |
| VoltageShift | latest | MSR power tuning |
| NVMeFix | latest | NVMe power management |
| RealtekCardReader | latest | SD card reader |
| YogaSMCAlter-L7210 | custom | Dell Latitude SMC |
| UTBMap-L7210 | custom | USB mapping Dell 7210 |
| USBToolBox | latest | USB framework |

---

## ⚡ Optimasi MSR yang Diterapkan

### MSR Aktif (Aman di Comet Lake-U)

| MSR | Nilai | Fungsi |
|-----|-------|--------|
| `0x1FC` | `0x0024005E` | BD PROCHOT **OFF** (blokir throttling 400 MHz) |
| `0x610` | PL1=PL2=55W | RAPL Power Limit dibuka dari 15W ke 55W |
| `0x774` | `0x00313112` | HWP Request: EPP=0x00 (Max Performance), floor 1.8 GHz |

### ⛔ MSR BERBAHAYA — JANGAN DISENTUH

| MSR | Alasan |
|-----|--------|
| `0x772` | Menyebabkan **Kernel Panic #GP Type 13** di Comet Lake-U |
| `0x773` | Sama — crash langsung |

> **PENTING:** Wrapper `/usr/local/bin/voltageshift` (atau `~/.local/bin/voltageshift`) secara otomatis memblokir akses ke MSR 0x772 dan 0x773. Jangan gunakan binary `voltageshift-raw` langsung tanpa wrapper.

---

## 🗂️ Struktur Backup

```
hackintosh-backup/
├── EFI/                    # Partisi EFI lengkap (OpenCore)
│   ├── OC/
│   │   ├── config.plist
│   │   ├── Kexts/
│   │   ├── ACPI/
│   │   └── Drivers/
│   └── BOOT/
├── scripts/                # Skrip optimasi native
│   ├── dell-logguard.sh    # Guardian: PL/PROCHOT/HWP/AirDrop (interval 30 menit)
│   ├── ram-warmup.sh       # Pre-warm RAM + SQLite maintenance
│   ├── optimize-sleep.sh   # Power/sleep settings
│   └── voltageshift        # Wrapper keamanan MSR (bash)
├── launchagents/           # LaunchAgent plist (auto-start)
│   ├── com.dell7210.logguard.plist
│   ├── com.dell7210.ramwarmup.plist
│   ├── com.dell7210.jackfix.plist
│   ├── com.dell7210.smartappsleeper.plist
│   ├── com.dell7210.smarttouchpointer.plist
│   └── com.dell7210.modemsmartfren.plist
├── firefox/
│   └── user.js             # Optimasi Firefox (scrolling, media, proses)
├── docs/
│   └── plan_penanganan_log_hackintosh.md
└── README.md               # File ini
```

---

## 🔧 Cara Restore EFI

### Prasyarat
1. Buat USB installer macOS baru dengan OpenCore
2. Mount partisi EFI target: `sudo diskutil mount EFI`
3. Backup EFI lama dulu (opsional)

### Langkah Restore
```bash
# 1. Mount EFI partisi target (ganti diskXsY sesuai)
sudo diskutil mount /dev/disk0s1

# 2. Hapus EFI lama (hati-hati!)
sudo rm -rf /Volumes/EFI/EFI/

# 3. Copy EFI dari backup ini
sudo cp -R /Volumes/RESCUE1302/hackintosh-backup/EFI/ /Volumes/EFI/EFI/

# 4. Verifikasi
ls /Volumes/EFI/EFI/OC/
```

### Restore Scripts & LaunchAgents
```bash
# 1. Copy scripts
mkdir -p ~/.local/bin
cp /Volumes/RESCUE1302/hackintosh-backup/scripts/* ~/.local/bin/
chmod +x ~/.local/bin/*.sh
chmod +x ~/.local/bin/voltageshift

# 2. Copy LaunchAgents
cp /Volumes/RESCUE1302/hackintosh-backup/launchagents/*.plist ~/Library/LaunchAgents/

# 3. Load semua LaunchAgents
for plist in ~/Library/LaunchAgents/com.dell7210.*.plist; do
    launchctl load "$plist"
    echo "Loaded: $plist"
done

# 4. Restore Firefox user.js
FF_PROFILE=$(ls -d ~/Library/Application\ Support/Firefox/Profiles/*.default-release | head -1)
cp /Volumes/RESCUE1302/hackintosh-backup/firefox/user.js "$FF_PROFILE/"
```

---

## 🚀 Konfigurasi Power & Performa

### pmset (Baterai)
```
lidwake=0, sleep=15, displaysleep=5
```

### pmset (AC)
```
sleep=0, displaysleep=10
```

### Login Window
```
PowerButtonSleepsSystem = true
```

### OCSP (cold start fix)
```
com.apple.security.revocation OCSPStyle = None
```

### AirDrop (logd storm fix)
```
DiscoverableMode = Off
```

---

## 📌 Catatan Penting

- **OC Lock aktif**: Voltage offset tidak bisa diubah, hanya power limit
- **TRIM aktif**: KIOXIA NVMe TRIM diaktifkan manual (`trimforce enable`)
- **GPU**: Metal aktif, H.264 + HEVC hardware decode aktif
- **RAM**: 16GB LPDDR3, tidak upgradeable (soldered)
- **Keyboard/Mouse**: Bluetooth eksternal digunakan karena form factor tablet
- Docker berjalan: `bengkel-ops-postgres-local` (port 5433), `bengkel-ops-postgres` (port 55435)

---

## 🔗 Referensi

- [OpenCore Guide](https://dortania.github.io/OpenCore-Install-Guide/)
- [Dortania Comet Lake](https://dortania.github.io/OpenCore-Install-Guide/config-laptop.plist/coffee-lake-plus.html)
- [VoltageShift GitHub](https://github.com/sicreative/VoltageShift)
- [CPUFriend Guide](https://dortania.github.io/OpenCore-Post-Install/universal/pm.html)
