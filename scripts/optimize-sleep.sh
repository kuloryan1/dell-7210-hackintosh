#!/bin/bash
# Optimal Sleep & Power settings for Dell Latitude 7210 2-in-1 on macOS Sonoma
# Menghilangkan DarkWake berlebih pada baterai dan mengaktifkan deep idle sleep

echo "Menerapkan konfigurasi manajemen daya hemat baterai..."

# Pengaturan saat menggunakan Baterai (-b)
sudo pmset -b displaysleep 5
sudo pmset -b sleep 15
sudo pmset -b disksleep 10
sudo pmset -b standby 0
sudo pmset -b tcpkeepalive 0
sudo pmset -b powernap 0
sudo pmset -b proximitywake 0
sudo pmset -b womp 0

# Pengaturan saat terhubung Charger AC (-c)
sudo pmset -c displaysleep 15
sudo pmset -c sleep 30
sudo pmset -c disksleep 10
sudo pmset -c standby 0
sudo pmset -c tcpkeepalive 0
sudo pmset -c powernap 0
sudo pmset -c proximitywake 0
sudo pmset -c womp 0

echo "Sukses: Konfigurasi daya berhasil diterapkan."
echo "Status daya saat ini:"
pmset -g custom
