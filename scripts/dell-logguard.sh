#!/bin/bash
# Dell Latitude 7210 - Native Log, Power, Responsiveness & BLE Guardian
# Menjaga sistem tetap dingin, responsif tanpa jeda, mencegah BD PROCHOT (throttling 400 MHz), dan peredam log

VSHIFT="${HOME}/.local/bin/voltageshift"
if [ ! -x "$VSHIFT" ]; then
    VSHIFT="/usr/local/bin/voltageshift"
fi

if [ -x "$VSHIFT" ]; then
    # 1. Buka Batas Daya (Power Limit PL1=55W, PL2=55W) agar CPU tidak tertahan di 15W
    "$VSHIFT" power 55 55 2>/dev/null || true

    # 2. Nonaktifkan BD PROCHOT (Mencegah penguncian darurat 400 MHz oleh EC)
    "$VSHIFT" write 0x1FC 0x0024005E 2>/dev/null || true
    
    # 3. Optimalisasi Responsivitas Maksimal HWP (EPP 0x00 Raw Performance, Min Floor 1.8 GHz, Max 4.9 GHz)
    # CPU tidak akan turun ke 400 MHz dan langsung responsif instan
    for _ in {1..8}; do
        "$VSHIFT" write 0x774 0x00313112 2>/dev/null || true
    done
fi

# 3. Pastikan AirDrop DiscoverableMode tetap "Off" (mencegah loop Intel BLE scanning)
CURRENT_AIRDROP=$(defaults read com.apple.sharingd DiscoverableMode 2>/dev/null)
if [ "$CURRENT_AIRDROP" != "Off" ]; then
    defaults write com.apple.sharingd DiscoverableMode -string "Off"
    killall sharingd 2>/dev/null || true
fi

# 4. Pantau CPU logd secara preventif
# Jika logd mengalami spike abnormal (> 40% CPU), catat dan redam
LOGD_PID=$(pgrep -x logd 2>/dev/null)
if [ -n "$LOGD_PID" ]; then
    LOGD_CPU=$(ps -p "$LOGD_PID" -o %cpu= 2>/dev/null | tr -d ' ' | cut -d'.' -f1)
    if [ -n "$LOGD_CPU" ] && [ "$LOGD_CPU" -gt 40 ]; then
        killall -HUP logd 2>/dev/null || true
    fi
fi

# 5. Pastikan tombol power mengaktifkan Sleep
defaults write com.apple.loginwindow PowerButtonSleepsSystem -bool true 2>/dev/null || true

# 6. Bersihkan file crash & laporan diagnostik usang milik user (> 3 hari)
find "$HOME/Library/Logs/DiagnosticReports" -name "*.diag" -mtime +3 -delete 2>/dev/null || true
find "$HOME/Library/Logs/DiagnosticReports" -name "*.ips" -mtime +3 -delete 2>/dev/null || true

exit 0
