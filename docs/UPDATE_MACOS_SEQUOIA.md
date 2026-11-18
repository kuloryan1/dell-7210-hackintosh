# Panduan Lengkap & Aman Update ke macOS Sequoia (15.x)

Dokumen ini memandu proses pembaruan sistem operasi dari macOS Sonoma ke **macOS Sequoia (15.x)** pada **Dell Latitude 7210 2-in-1** tanpa risiko bootloop atau crash kext.

---

## ⚡ 1. Kesiapan EFI untuk macOS Sequoia

Folder EFI di repositori ini telah dioptimasi dan diverifikasi siap menjalankan macOS Sequoia (Darwin 24.x):
1. **Batas Kernel (MaxKernel) Terbuka**: Kext inti (`Lilu`, `VirtualSMC`, `WhateverGreen`, `AppleALC`, `VoodooI2C`, `VoodooPS2Controller`, `USBToolBox`) telah dikonfigurasi tanpa pembatasan `MaxKernel`, sehingga otomatis aktif di kernel Darwin 24.x.
2. **Penanganan Wi-Fi Intel Dual-Boot**:
   - Di **Sonoma**: Menggunakan `AirportItlwm.kext` (menu bar Wi-Fi bawaan macOS aktif).
   - Di **Sequoia**: Disarankan beralih ke `itlwm.kext` + **HeliPort.app** untuk menghindari crash driver dan lonjakan CPU akibat loop AirDrop.
3. **Mode Verbose (`-v`) Aktif**: Memastikan teks log proses instalasi terlihat jelas di layar selama reboot berulang.

---

## 📋 2. Langkah-Langkah Update

### Tahap 1: Persiapan
1. Pastikan Dell Latitude 7210 terhubung ke charger (AC adapter).
2. Sediakan ruang kosong di partisi SSD macOS minimal **30 GB – 40 GB**.
3. Buat cadangan partisi EFI Anda saat ini ke flashdisk darurat.

### Tahap 2: Memulai Pembaruan Sistem
1. Masuk ke **System Settings** > **General** > **Software Update**.
2. Ketika opsi update **macOS Sequoia** muncul, klik **Upgrade Now**.
3. macOS akan mengunduh paket instalasi (sekitar 12 – 14 GB).

### Tahap 3: Proses Reboot & Instalasi (PENTING)
1. Setelah pengunduhan selesai, sistem akan meminta restart.
2. Saat laptop menyala kembali dan masuk ke menu OpenCore Boot Picker:
   - Biarkan OpenCore memilih entri instalasi otomatis (bernama **`macOS Installer`**).
   - **JANGAN mematikan laptop secara paksa.**
   - Laptop akan melakukan reboot otomatis **2 hingga 4 kali**.
3. Di setiap reboot, biarkan sistem berjalan sampai akhirnya masuk kembali ke desktop dengan nama partisi disk utama Anda.

---

## 📶 3. Mengatur Wi-Fi di macOS Sequoia (HeliPort)

Jika di macOS Sequoia Anda memilih menggunakan `itlwm.kext`:
1. Buka folder **Applications** > buka **HeliPort.app**.
2. Ikon Wi-Fi HeliPort akan muncul di menu bar kanan atas layar.
3. Klik ikon tersebut, pilih SSID Wi-Fi Anda, lalu masukkan password.
4. **Jadikan Otomatis Saat Boot**:
   - Masuk ke **System Settings** > **General** > **Login Items**.
   - Tambahkan **HeliPort** ke daftar agar aplikasi Wi-Fi langsung aktif setiap laptop dinyalakan.

---

## 🛡️ 4. Langkah Penyelamatan (Rollback)

Jika terjadi kendala saat proses update:
1. Hubungkan flashdisk rescue (dengan EFI sebelum update).
2. Nyalakan laptop, tekan **F12**, pilih boot dari flashdisk UEFI.
3. Buka Terminal Recovery dan pulihkan EFI cadangan Anda.
