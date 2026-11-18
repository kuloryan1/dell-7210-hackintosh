#!/bin/bash
# Script instalasi otomatis skrip optimasi & LaunchAgents untuk Dell Latitude 7210
set -e

echo "=== Instalasi Skrip Optimasi & Service Dell 7210 ==="

# 1. Buat folder target jika belum ada
mkdir -p "$HOME/.local/bin"
mkdir -p "$HOME/Library/LaunchAgents"

# 2. Salin skrip optimasi ke ~/.local/bin
echo "[1/4] Menyalin skrip optimasi ke $HOME/.local/bin..."
cp scripts/dell-logguard.sh "$HOME/.local/bin/"
cp scripts/optimize-sleep.sh "$HOME/.local/bin/"
cp scripts/ram-warmup.sh "$HOME/.local/bin/"
cp scripts/voltageshift "$HOME/.local/bin/"
chmod +x "$HOME/.local/bin/"*.sh
chmod +x "$HOME/.local/bin/voltageshift"

# 3. Salin & sesuaikan username pada file LaunchAgents plist
echo "[2/4] Menyesuaikan direktori home pada LaunchAgents..."
for plist in launchagents/*.plist; do
    filename=$(basename "$plist")
    sed "s|/Users/[^/]*|$HOME|g" "$plist" > "$HOME/Library/LaunchAgents/$filename"
done

# 4. Berikan izin eksekusi dan load LaunchAgent logguard
echo "[3/4] Mengaktifkan Guardian Service..."
launchctl unload "$HOME/Library/LaunchAgents/com.dell7210.logguard.plist" 2>/dev/null || true
launchctl load "$HOME/Library/LaunchAgents/com.dell7210.logguard.plist" 2>/dev/null || true

# 5. Jalankan optimasi awal
echo "[4/4] Menerapkan pengaturan awal (AirDrop fix, Power button sleep, dsb)..."
"$HOME/.local/bin/dell-logguard.sh" || true

echo "=== Selesai! Layanan guardian aktif dan memantau di latar belakang. ==="
