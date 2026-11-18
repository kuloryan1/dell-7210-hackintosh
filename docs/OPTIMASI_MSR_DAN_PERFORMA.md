# Panduan Optimasi MSR, Manajemen Daya, & Pencegahan Panic

Dokumen ini menjelaskan secara mendalam tentang optimasi performa prosesor Intel Core i7-10610U (Comet Lake-U) pada **Dell Latitude 7210 2-in-1**, cara mengatasi throttling ekstrem khas Dell, serta peringatan keselamatan fatal terkait MSR register.

---

## 🛑 1. Masalah Khas Dell: Throttling 400 MHz (BD PROCHOT)

### Gejala Masalah
Saat laptop digunakan, tiba-tiba sistem menjadi sangat patah-patah (lag parah), animasi tersendat, mouse bergerak lambat, dan CPU terasa "tercekik". Jika diperiksa di monitor aktivitas atau Intel Power Gadget:
- Frekuensi CPU terkunci di **0.4 GHz (400 MHz)**.
- Konsumsi daya prosesor (CPU Package Power) turun drastis ke **~4 Watt**.
- Beban CPU tampak 100% padahal tidak ada aplikasi berat yang berjalan.

### Penyebab Teknis
Laptop Dell 2-in-1 menggunakan mekanisme perlindungan **BD PROCHOT (Bi-Directional Processor Hot)** yang dikendalikan oleh chip Embedded Controller (EC). Sinyal ini dapat dipicu secara palsu oleh:
1. Suhu VRM atau port USB-C saat pengisian daya cepat.
2. Perubahan profil daya charger Type-C yang tidak dikenali sebagai charger original Dell 65W.
3. Bug sinyal power state di macOS.

Ketika BD PROCHOT menyala, EC memaksa prosesor turun ke frekuensi operasi terendah (P-State terendah = 400 MHz) tanpa memperdulikan suhu sebenarnya dari core CPU.

### Solusi Permanen
Kita menonaktifkan bit kontrol BD PROCHOT pada register MSR `0x1FC`:
```bash
# Nilai aman untuk menonaktifkan bit 0 (BD PROCHOT):
voltageshift write 0x1FC 0x0024005E
```
Setelah perintah ini dijalankan, prosesor seketika terbebas dari kunci 400 MHz dan melesat kembali ke frekuensi normal hingga turbo boost (>3.5 GHz).

---

## ⚡ 2. Membuka Batas Daya (Power Limit PL1 / PL2) ke 55 Watt

Secara default dari pabrik Dell, prosesor i7-10610U dibatasi pada:
- **PL1 (Batas Jangka Panjang)**: 15 Watt
- **PL2 (Batas Boost Singkat)**: 25 Watt

Batas ini membuat performa CPU cepat drop saat melakukan kompilasi kode, rendering video, atau membuka banyak tab browser.

Melalui register MSR `0x610` (RAPL Power Limit), batas daya dibuka menjadi **55 Watt**:
```bash
voltageshift power 55 55
```
Dengan membuka batas daya ini, prosesor dapat mempertahankan frekuensi turbo lebih lama dengan suhu operasi yang tetap terkontrol (~55°C – 65°C pada beban normal).

---

## 🚀 3. HWP SpeedShift Tuning (EPP 0x00)

Teknologi Intel SpeedShift (HWP) mengatur seberapa agresif prosesor menaikkan clock saat menerima beban kerja.
Melalui register MSR `0x774`, kita mengonfigurasi:
- **EPP (Energy Performance Preference)**: `0x00` (Maximum Performance / Tanpa Jeda)
- **Minimum Floor**: 1.8 GHz
- **Maximum Boost**: 4.9 GHz

```bash
for _ in {1..8}; do
    voltageshift write 0x774 0x00313112
done
```
Hasilnya: Transisi clock CPU menjadi sangat instan tanpa lag responsivitas.

---

## ⛔ 4. PERINGATAN BAHAYA: Kernel Panic #GP Type 13

> [!CAUTION]
> ### JANGAN PERNAH MENYENTUH MSR `0x772` DAN `0x773`!
> 
> Pada prosesor Intel Comet Lake-U (Generasi 10), register MSR `0x772` dan `0x773` **TIDAK DIDUKUNG OLEH HARDWARE**.
> 
> Jika Anda atau script pihak ketiga mencoba membaca atau menulis ke `0x772` atau `0x773`:
> 1. Prosesor Intel akan melemparkan interupsi perangkat keras: **General Protection Exception (#GP Type 13)**.
> 2. Kernel macOS langsung mengalami **Fatal Kernel Panic**.
> 3. Layar mati mendadak dan laptop restart seketika.

### Skrip Pengaman (Safety Wrapper)
Untuk mencegah insiden ini, repositori ini menyertakan script wrapper di [`scripts/voltageshift`](file:///Users/kuloryan/Documents/Github/Dell%207210/scripts/voltageshift):
```bash
# Cuplikan filter pengaman:
for arg in "$@"; do
    case "$arg" in
        0x772|0x773|772|773|0X772|0X773)
            echo "Akses Ditolak: MSR $arg diblokir demi mencegah Kernel Panic." >&2
            exit 1
            ;;
    esac
done
```
Selalu gunakan wrapper ini saat berinteraksi dengan MSR di terminal atau otomasi.

---

## 🛠️ 5. Otomasi Latar Belakang: `dell-logguard`

Semua perbaikan di atas (BD PROCHOT, Power Limit 55W, HWP tuning) telah diintegrasikan ke dalam script [`scripts/dell-logguard.sh`](file:///Users/kuloryan/Documents/Github/Dell%207210/scripts/dell-logguard.sh) dan dijalankan secara otomatis setiap 30 menit serta saat login melalui LaunchAgent [`launchagents/com.dell7210.logguard.plist`](file:///Users/kuloryan/Documents/Github/Dell%207210/launchagents/com.dell7210.logguard.plist).

Cukup jalankan script installer:
```bash
bash scripts/install-launchagents.sh
```
Maka laptop Dell Latitude 7210 Anda akan selalu terlindungi dari throttling secara otomatis.
