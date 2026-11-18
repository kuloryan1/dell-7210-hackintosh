# Panduan Lengkap Instalasi Hackintosh untuk Pemula (Dell Latitude 7210 2-in-1)

Panduan ini dibuat secara terstruktur, ramah pemula, dan langkah demi langkah agar Anda dapat menginstal macOS (Sonoma atau Sequoia) pada **Dell Latitude 7210 2-in-1** dengan lancar dan aman.

---

## 🧰 1. Persiapan & Kebutuhan

1. **Laptop**: Dell Latitude 7210 2-in-1 (Intel Core i5/i7 Generasi 10 Comet Lake-U).
2. **Flashdisk**: Minimal 16 GB (USB 3.0 disarankan agar proses cepat).
3. **Koneksi Internet**: Untuk download installer macOS dan paket pendukung.
4. **Charger Original**: Selalu hubungkan laptop ke charger selama proses instalasi.

---

## ⚙️ 2. Pengaturan BIOS Dell Latitude 7210

Nyalakan laptop, segera tekan tombol **F2** berulang kali untuk masuk ke menu BIOS Setup. Pastikan opsi-opsi berikut diatur dengan benar:

| Menu BIOS | Opsi Pengaturan | Nilai / Status | Catatan Penting |
| :--- | :--- | :--- | :--- |
| **System Configuration** | **SATA Operation** | **AHCI** | Wajib! Jika masih RAID On, installer tidak akan mendeteksi SSD. |
| **Security** | **Secure Boot** | **Disabled** | Wajib dinonaktifkan agar OpenCore dapat di-boot. |
| **Security** | **Intel SGX** | **Disabled** | Mencegah konflik alokasi memori. |
| **Virtualization** | **Intel Virtualization Technology** | **Enabled** | Mengaktifkan VT-x untuk virtualisasi. |
| **Virtualization** | **VT for Direct I/O (VT-d)** | **Enabled / Disabled** | EFI ini sudah dilengkapi patch `DisableIoMapper`. |
| **Power Management** | **Block Sleep** | **Disabled** | Jangan centang agar sleep macOS berfungsi. |
| **POST Behavior** | **Fastboot** | **Thorough** | Memastikan hardware diinisialisasi lengkap saat boot. |

*Tekan **Apply Changes** lalu **Exit**.*

---

## 💾 3. Membuat USB Installer macOS

Anda bisa membuat USB Installer menggunakan komputer Windows, Linux, maupun Mac yang sudah ada:

### Menggunakan Windows:
1. Download installer macOS recovery menggunakan tool resmi [gibMacOS](https://github.com/corpnewt/gibMacOS).
2. Gunakan script `MakeInstall.py` di dalam gibMacOS untuk memformat flashdisk menjadi 2 partisi: Partisi FAT32 EFI dan partisi installer macOS.

### Menggunakan Mac:
1. Download installer macOS Sonoma atau Sequoia dari Mac App Store.
2. Buat installer resmi ke flashdisk via Terminal:
   ```bash
   sudo /Applications/Install\ macOS\ Sonoma.app/Contents/Resources/createinstallmedia --volume /Volumes/MyVolume
   ```

---

## 📁 4. Memasang Folder EFI ke Flashdisk

1. Mount partisi EFI pada flashdisk Anda:
   - Di Windows: Gunakan tool `Explorer++` (Run as Administrator) atau `MountEFI`.
   - Di macOS: Gunakan tool `MountEFI` atau via terminal:
     ```bash
     sudo diskutil mount /dev/diskXs1
     ```
2. Salin seluruh isi folder [`EFI/`](file:///Users/kuloryan/Documents/Github/Dell%207210/EFI) dari repositori ini ke dalam partisi EFI flashdisk Anda:
   ```
   Partisi EFI Flashdisk/
   └── EFI/
       ├── BOOT/
       │   └── BOOTx64.efi
       └── OC/
           ├── ACPI/
           ├── Drivers/
           ├── Kexts/
           ├── OpenCore.efi
           └── config.plist
   ```

---

## 🔑 5. Wajib: Generate Serial Number (SMBIOS) Baru

> [!IMPORTANT]
> **JANGAN gunakan serial number bawaan file config.plist mentah-mentah!**
> Jika banyak orang menggunakan serial number yang sama, Apple ID Anda bisa terkena blokir atau iMessage/FaceTime tidak bisa aktif.

1. Download tool [GenSMBIOS](https://github.com/corpnewt/GenSMBIOS).
2. Jalankan `GenSMBIOS.command` (atau `GenSMBIOS.bat` di Windows).
3. Pilih opsi **Generate SMBIOS**.
4. Masukkan model: **`MacBookPro16,3`**.
5. Buka `EFI/OC/config.plist` menggunakan editor seperti [ProperTree](https://github.com/corpnewt/ProperTree).
6. Masuk ke bagian **`PlatformInfo -> Generic`**:
   - Ganti **SystemSerialNumber** dengan serial number baru hasil generate.
   - Ganti **MLB** (Board Serial) dengan MLB baru hasil generate.
   - Ganti **SystemUUID** (SmUUID) dengan UUID baru hasil generate.
7. Simpan file `config.plist`.

---

## 🚀 6. Memulai Proses Instalasi

1. Colokkan flashdisk ke port USB Type-A Dell Latitude 7210.
2. Nyalakan laptop, tekan tombol **F12** berulang kali untuk membuka **One-Time Boot Menu**.
3. Pilih opsi **UEFI: [Nama Flashdisk Anda]**.
4. Menu bootloader OpenCore akan muncul. Pilih entri **Install macOS Sonoma** (atau Sequoia).
5. Layar teks verbose (`-v`) akan berjalan selama 1-2 menit sebelum masuk ke layar utama macOS Recovery.
6. **Format SSD Internal**:
   - Buka **Disk Utility**.
   - Klik menu **View** di kiri atas, pilih **Show All Devices**.
   - Pilih disk fisik SSD utama laptop Anda (bukan volume di bawahnya).
   - Klik **Erase**:
     - Name: `Macintosh HD`
     - Format: **APFS**
     - Scheme: **GUID Partition Map**
   - Klik Erase, tunggu hingga selesai, lalu tutup Disk Utility.
7. **Pilih Reinstall / Install macOS**:
   - Pilih disk `Macintosh HD` yang baru saja diformat.
   - Klik Continue.

> [!NOTE]
> Laptop akan melakukan restart otomatis sebanyak **2 hingga 4 kali**. Ini adalah proses yang normal!
> Setiap kali laptop reboot, biarkan sistem memilih entri otomatis di menu OpenCore (biasanya bernama *"macOS Installer"* atau *"Macintosh HD"*). **Jangan cabut flashdisk sampai Anda benar-benar masuk ke desktop macOS!**

---

## 🏁 7. Pasca Instalasi (Post-Install)

Setelah berhasil masuk ke desktop macOS:

### 1. Pindahkan EFI Flashdisk ke SSD Internal
Agar laptop dapat menyala tanpa perlu mencolokkan flashdisk terus-menerus:
1. Mount partisi EFI pada flashdisk dan partisi EFI pada SSD internal.
2. Salin folder `EFI` dari flashdisk ke partisi EFI SSD internal.

### 2. Pasang Skrip Optimasi & Service Guardian
Buka aplikasi **Terminal** di macOS, masuk ke folder repositori ini dan jalankan:
```bash
bash scripts/install-launchagents.sh
bash scripts/optimize-sleep.sh
```

### 3. Aktifkan TRIM SSD
```bash
sudo trimforce enable
```
*(Tekan `y` saat diminta konfirmasi, laptop akan restart otomatis).*

Laptop Dell Latitude 7210 2-in-1 Anda kini telah siap digunakan dengan stabil, dingin, dan optimal!
