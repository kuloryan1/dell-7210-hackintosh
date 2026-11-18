#!/bin/bash
# Pre-warm application binaries into macOS Unified Buffer Cache (RAM)
# dan pemeliharaan otomatis ChatGPT SQLite di latar belakang (nice -n 20)

# 1. Kunci Shutter Speed Kamera Dell 7210 (Cepat & instan, cegah drop ke 15 FPS di ruangan gelap)
if [ -x "$HOME/.local/bin/dell-camera-boost" ]; then
    nice -n 20 "$HOME/.local/bin/dell-camera-boost" --lock30 > /dev/null 2>&1 || true
fi

# 2. Pemeliharaan otomatis database ChatGPT / Codex (ringan & instan < 20ms)
if [ -f "$HOME/.codex/logs_2.sqlite" ]; then
    nice -n 20 sqlite3 "$HOME/.codex/logs_2.sqlite" "DELETE FROM logs WHERE id < (SELECT max(id) - 1000 FROM logs); PRAGMA wal_checkpoint(TRUNCATE);" 2>/dev/null || true
fi

if [ -f "$HOME/.codex/thread_history_1.sqlite" ]; then
    nice -n 20 sqlite3 "$HOME/.codex/thread_history_1.sqlite" "PRAGMA wal_checkpoint(TRUNCATE);" 2>/dev/null || true
fi

# 3. Smart Staggered App Pre-Warm & Signature Cache (Latar Belakang - Prioritas Terendah)
# Membaca binary dan memvalidasi signature di background saat CPU idle (60s setelah login)
# Efek: Saat Anda mengklik WhatsApp, Firefox, dll, app langsung terbuka instan (klik langsung muncul)
(
    sleep 60
    TARGET_APPS=(
        "/Applications/WhatsApp.app"
        "/Applications/Firefox.app"
        "/Applications/ChatGPT.app"
        "/Applications/Antigravity.app"
    )

    for app in "${TARGET_APPS[@]}"; do
        if [ -d "$app" ]; then
            # 1. Masukkan file executable utama ke RAM buffer cache
            bin_name=$(defaults read "$app/Contents/Info.plist" CFBundleExecutable 2>/dev/null)
            if [ -n "$bin_name" ] && [ -f "$app/Contents/MacOS/$bin_name" ]; then
                nice -n 20 cat "$app/Contents/MacOS/$bin_name" > /dev/null 2>&1 || true
            fi
            
            # 2. Pemanasan verifikasi signature (syspolicyd trust cache)
            nice -n 20 codesign -v "$app" > /dev/null 2>&1 || true
            
            # Beri jeda 1 detik agar CPU dan suhu tetap dingin
            sleep 1
        fi
    done
) >/dev/null 2>&1 &
