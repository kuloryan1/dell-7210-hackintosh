#!/usr/bin/env bash
# Read hardware and save NEW result files beside this launcher.
# Does not format, repair, repartition, or mount any device.
set -euo pipefail

task_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)"
if [[ "$(uname -s)" != Linux ]]; then
    printf '%s\n' 'Jalankan dari Linux live yang di-boot langsung pada Dell.' >&2
    exit 1
fi
if [[ "$(id -u)" != 0 ]]; then
    printf '%s\n' 'Akses root diperlukan. Jalankan: sudo bash JALANKAN-AUDIT.sh' >&2
    exit 1
fi
command -v python3 >/dev/null || { printf '%s\n' 'Python 3 belum tersedia; gunakan image SystemRescue yang disiapkan.' >&2; exit 1; }
command -v findmnt >/dev/null || { printf '%s\n' 'findmnt tidak tersedia; periksa media tujuan secara manual.' >&2; exit 1; }
task_fs="$(findmnt --noheadings --output FSTYPE --target "$task_dir")"
task_opts="$(findmnt --noheadings --output OPTIONS --target "$task_dir")"
case "$task_fs" in
    tmpfs|ramfs|overlay|squashfs|iso9660)
        printf '%s\n' 'Folder ini berada di RAM atau image baca-saja. Salin HACKINTOSH-AUDIT ke media simpan yang dapat ditulis terlebih dahulu.' >&2
        exit 1
        ;;
esac
case ",$task_opts," in
    *,ro,*)
        printf '%s\n' 'Media tujuan masih dipasang baca-saja. Periksa mount media USB sebelum menyimpan hasil; launcher tidak melakukan remount otomatis.' >&2
        findmnt --target "$task_dir" >&2
        exit 1
        ;;
esac
if [[ ! -w "$task_dir" ]]; then
    printf '%s\n' 'Folder tujuan tidak dapat ditulis. Pilih folder media simpan yang sesuai.' >&2
    exit 1
fi
task_stamp="$(date -u +%Y%m%d-%H%M%S)-$$"
task_output="$task_dir/hasil-linux-$task_stamp"
python3 "$task_dir/Collect-LinuxHardware.py" --output "$task_output"
printf '\n%s\n%s\n' 'Simpan ZIP ini sebelum keluar dari Linux live:' "$task_output.zip"

