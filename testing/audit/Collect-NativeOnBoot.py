#!/usr/bin/env python3
"""Run the reviewed hardware collector on its approved SystemRescue boot USB.

The only mount change allowed is remounting the already mounted boot USB rw,
after verifying the physical disk transport, exact size, filesystem, model and
media marker. No other disk is mounted, repaired, partitioned or formatted.
"""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import zipfile

MODEL = 'Latitude 7210 2-in-1'
USB_BYTES = 62723719168
COLLECTOR_SHA256 = 'ab20f210507db93cc9be6d2cc8f2fb589630180fff12ecd263c74467f9f124d1'
BOOT = Path('/run/archiso/bootmnt')


def command_json(command):
    reply = subprocess.run(command, capture_output=True, text=True, timeout=20, check=True)
    return json.loads(reply.stdout)


def require_usb_target(blocks, source):
    """Return the physical USB ancestor only for the approved whole-disk size."""
    source = os.path.realpath(source)

    def search(nodes, physical=None):
        for node in nodes:
            disk = node if node.get('type') == 'disk' else physical
            path = node.get('path')
            if path and os.path.realpath(path) == source:
                return disk
            found = search(node.get('children', []), disk)
            if found:
                return found
        return None

    disk = search(blocks.get('blockdevices', []))
    if not disk or disk.get('type') != 'disk' or disk.get('tran') != 'usb' or int(disk.get('size', 0)) != USB_BYTES:
        raise RuntimeError('Boot source is not the approved 62723719168-byte USB disk; no media writes performed.')
    return disk


def save_json(path, data):
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(data, indent=2), encoding='utf-8')
    temporary.replace(path)


def compare_windows(folder, baseline):
    native = json.loads((folder / 'linux-inventory.json').read_text())
    tables = native.get('ACPITables', [])
    native_ssdt = {t['SHA256'].lower() for t in tables if t['Signature'] == 'SSDT'}
    native_dsdt = {t['SHA256'].lower() for t in tables if t['Signature'] == 'DSDT'}
    known_ssdt = {h.lower() for h in baseline['KnownSSDT_SHA256']}
    return {
        'BIOSMatchesWindows': native.get('DMI', {}).get('bios_version') == baseline['BIOSVersion'],
        'DSDTMatchesWindows': baseline['DSDT_SHA256'].lower() in native_dsdt,
        'AllKnownWindowsSSDTsFound': known_ssdt.issubset(native_ssdt),
        'WindowsExpectedSSDT': baseline['ExpectedSSDTCount'],
        'NativeUniqueSSDT': len(native_ssdt),
        'NativeSSDTNotInWindowsExport': len(native_ssdt - known_ssdt),
        'BadStandardACPIChecksums': [t['File'] for t in tables if t.get('ChecksumApplicable') and not t.get('ChecksumValid')],
        'AudioCodecFiles': len(list((folder / 'audio-codecs').glob('*.txt'))),
        'HIDDescriptorFiles': len(list((folder / 'hid-report-descriptors').glob('*.bin'))),
        'USBDescriptorFiles': len(list((folder / 'usb-descriptors').glob('*.bin'))),
        'CFGLockStatus': native.get('PlatformReadings', {}).get('CFGStatus', 'UNKNOWN'),
        'GraphicsPreallocatedMiB': native.get('PlatformReadings', {}).get('GraphicsPreallocation', {}).get('GraphicsStolenPreallocatedMiB'),
        'IIOSensorsFound': len(native.get('IIOSensors', [])),
        'CollectionWarnings': native.get('Notes', []),
        'MacOSFunctionalityTested': False,
        'Limit': 'Compare raw files and firmware identity before declaring ACPI coverage complete; this is not a macOS test.'
    }


def main():
    if sys.platform != 'linux' or os.geteuid() != 0:
        raise RuntimeError('Run as root in native Linux on the Dell.')
    release = Path('/proc/sys/kernel/osrelease').read_text().lower()
    if 'microsoft' in release or 'wsl' in release:
        raise RuntimeError('WSL does not expose the required physical firmware tables.')
    if Path('/sys/class/dmi/id/product_name').read_text().strip() != MODEL:
        raise RuntimeError('Unexpected computer model; collection was not started.')
    info = command_json(['findmnt', '--json', '--output', 'SOURCE,TARGET,FSTYPE,OPTIONS', '--target', str(BOOT)])
    mounts = info.get('filesystems', [])
    if len(mounts) != 1:
        raise RuntimeError('Cannot uniquely identify the live boot filesystem.')
    mount = mounts[0]
    source = mount.get('source', '')
    if mount.get('target') != str(BOOT) or mount.get('fstype') != 'vfat' or not source.startswith('/dev/'):
        raise RuntimeError('Expected the original writable-capable FAT32 boot USB, not an ISO/loop/RAM source.')
    blocks = command_json(['lsblk', '--json', '--bytes', '--output', 'NAME,PATH,TYPE,TRAN,SIZE'])
    require_usb_target(blocks, source)
    directory = BOOT / 'HACKINTOSH-AUDIT'
    marker = json.loads((directory / 'MEDIA-IDENTITY.json').read_text())
    if marker.get('Purpose') != 'Native Dell Hackintosh hardware collection' or marker.get('USBBytes') != USB_BYTES or marker.get('AllowedModel') != MODEL:
        raise RuntimeError('Approved collection marker is absent or incorrect.')
    collector = directory / 'Collect-LinuxHardware.py'
    if hashlib.sha256(collector.read_bytes()).hexdigest() != COLLECTOR_SHA256:
        raise RuntimeError('Hardware collector integrity check failed; execution refused.')
    if 'ro' in mount.get('options', '').split(','):
        # This changes only the mount mode of the validated boot USB.
        subprocess.run(['mount', '-o', 'remount,rw', str(BOOT)], check=True, timeout=20)
    after = command_json(['findmnt', '--json', '--output', 'SOURCE,TARGET,FSTYPE,OPTIONS', '--target', str(BOOT)])['filesystems'][0]
    if after.get('fstype') != 'vfat' or 'rw' not in after.get('options', '').split(',') or os.path.realpath(after.get('source', '')) != os.path.realpath(source):
        raise RuntimeError('The validated boot USB is not writable; collection output was not created.')
    stamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S') + '-' + str(os.getpid())
    output = directory / ('hasil-linux-' + stamp)
    log = directory / ('native-console-' + stamp + '.txt')
    status_file = directory / 'LATEST-NATIVE-STATUS.json'
    state = {'State': 'collecting', 'StartedAtUtc': datetime.now(timezone.utc).isoformat(),
             'Model': MODEL, 'OutputDirectory': output.name,
             'USBBytes': USB_BYTES, 'MacOSFunctionalityTested': False}
    save_json(status_file, state)
    try:
        # Allow standard kernel/udev probing to settle; no drivers/modules are manually installed or loaded.
        subprocess.run(['udevadm', 'settle', '--timeout=20'], capture_output=True, timeout=25, check=False)
        time.sleep(3)
        print('MENGAMBIL DATA HARDWARE DELL. Tidak menginstal OS atau mengubah partisi.', flush=True)
        reply = subprocess.run([sys.executable, str(collector), '--output', str(output)],
                               capture_output=True, text=True, timeout=300, check=False)
        log.write_text(reply.stdout + reply.stderr, encoding='utf-8')
        if reply.returncode != 0:
            raise RuntimeError('Hardware collector exited with code ' + str(reply.returncode) + '; see ' + log.name)
        archive = output.with_suffix('.zip')
        with zipfile.ZipFile(archive) as zipped:
            if zipped.testzip() is not None:
                raise RuntimeError('Result ZIP failed its integrity check.')
        baseline = json.loads((directory / 'WINDOWS-BASELINE.json').read_text())
        comparison = compare_windows(output, baseline)
        comparison_path = directory / ('comparison-' + stamp + '.json')
        save_json(comparison_path, comparison)
        state.update({'State': 'complete', 'FinishedAtUtc': datetime.now(timezone.utc).isoformat(),
                      'ResultZIP': archive.name, 'ResultZIPSHA256': hashlib.sha256(archive.read_bytes()).hexdigest(),
                      'ComparisonFile': comparison_path.name, 'Comparison': comparison,
                      'CollectedDataRequiresReview': True})
        save_json(status_file, state)
        os.sync()
        print('\nAUDIT SELESAI - HASIL TERSIMPAN DI FLASHDISK', flush=True)
        print('HACKINTOSH-AUDIT/' + archive.name, flush=True)
        print('SSDT unik: ' + str(comparison['NativeUniqueSSDT']) + '; codec audio: ' + str(comparison['AudioCodecFiles'])
              + '; descriptor HID: ' + str(comparison['HIDDescriptorFiles']), flush=True)
        print('Descriptor USB: ' + str(comparison['USBDescriptorFiles']), flush=True)
        print('CFG Lock: ' + str(comparison['CFGLockStatus'])
              + '; graphics preallocated MiB: ' + str(comparison['GraphicsPreallocatedMiB']), flush=True)
        if comparison['CollectionWarnings']:
            print('CATATAN KOLEKSI: ' + '; '.join(comparison['CollectionWarnings']), flush=True)
        print('Kembali ke Windows untuk memeriksa hasil. Tidak ada reboot otomatis.', flush=True)
    except Exception as error:
        state.update({'State': 'failed', 'FinishedAtUtc': datetime.now(timezone.utc).isoformat(),
                      'Error': str(error), 'ConsoleLog': log.name})
        save_json(status_file, state)
        os.sync()
        raise


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print('AUDIT BELUM SELESAI: ' + str(error), file=sys.stderr, flush=True)
        raise SystemExit(1)
