# Dokumentasi Hasil Uji, Audit, & Riwayat Log Testing

Folder `testing/` ini berisi seluruh bukti autentik, rekaman log mentah, laporan audit perangkat keras, dan rekam jejak pengujian yang diekstraksi langsung dari flashdisk pengujian (`RESCUE1302`).

Semua berkas di sini dipertahankan sebagai transparansi penuh bagi komunitas dan teknisi Hackintosh.

---

## 📂 Struktur Direktori Testing

```
testing/
├── SysReport/           # Dump tabel hardware asli dari OpenCore SysReport
│   ├── ACPI/            # DSDT dan SSDT bawaan pabrik Dell Latitude 7210
│   ├── CPU/             # CPUInfo.txt (Spesifikasi mikroarsitektur Core i7-10610U)
│   ├── PCI/             # PCIInfo.txt (Alamat PCI seluruh kontroler hardware)
│   ├── GOP/             # GOPInfo.txt (Resolusi & informasi Graphics Output Protocol)
│   ├── Drivers/         # DriverImageNames.txt (Driver UEFI yang dimuat)
│   └── SMBIOS/          # Binary SMBIOS bawaan mesin
├── audit/               # Hasil audit komparasi Linux vs Windows baseline
│   ├── BACA-DULU.txt    # Panduan audit independen
│   ├── Collect-LinuxHardware.py  # Skrip pengumpul info hardware di live Linux
│   ├── comparison-*.json         # Hasil verifikasi ACPI, PCI, dan SSDT
│   ├── LATEST-NATIVE-STATUS.json # Ringkasan status integritas firmware
│   └── WINDOWS-BASELINE.json    # Ekstraksi baseline ACPI dari Windows asli
├── opencore-logs/       # 45 file log boot OpenCore (opencore-2026-*.txt)
│   └── # Merekam setiap tahapan debugging: kext injection, ACPI patching,
│       # dan penanganan panic dari 25 Oktober hingga 2 November.
├── config-history/      # Rekam jejak evolusi file config.plist selama perbaikan
│   ├── config.plist.backup_agdc_fix
│   ├── config.plist.backup_dim_fix
│   ├── config.plist.backup_full_display_fix
│   ├── config.plist.backup_usb_crash_fix
│   └── config.plist.bak_before_panic_fix
└── acpi-source/         # Berkas source DSL (SSDT-PNLF.dsl) untuk referensi dev
```

---

## 🔍 Cara Memanfaatkan Data Testing

1. **Memeriksa Alamat PCI Perangkat**:
   Buka [`testing/SysReport/PCI/PCIInfo.txt`](file:///Users/kuloryan/Documents/Github/Dell%207210/testing/SysReport/PCI/PCIInfo.txt) untuk melihat Vendor ID, Device ID, dan DevicePath setiap perangkat keras di Dell Latitude 7210.
2. **Memverifikasi Tabel ACPI Asli**:
   Folder [`testing/SysReport/ACPI/`](file:///Users/kuloryan/Documents/Github/Dell%207210/testing/SysReport/ACPI/) memuat `DSDT.aml` murni dari firmware pabrik Dell tanpa modifikasi apa pun. Berguna jika Anda ingin membuat patch SSDT kustom sendiri.
3. **Menganalisis Riwayat Boot & Debugging**:
   Folder [`testing/opencore-logs/`](file:///Users/kuloryan/Documents/Github/Dell%207210/testing/opencore-logs/) berisi 45 log OpenCore berurutan waktu. Anda dapat melihat bagaimana parameter kernel, kext Lilu, WhateverGreen, dan AppleALC diuji coba hingga mencapai kondisi stabil.
