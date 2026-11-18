#!/usr/bin/env python3
"""Collect hardware data from native Linux without changing firmware or disks.
No package installation, partition operations, ACPI overrides, register writes,
device resets, serial-number collection, network identifiers, or key export.
May load the bundled Linux msr module with allow_writes=off to read MSR E2.
"""
import argparse
from datetime import datetime, timezone
import glob
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import struct
import subprocess
import sys
import zipfile


def read_text(path):
    try:
        return Path(path).read_text(errors='replace').strip()
    except OSError:
        return None


def collect_hid_descriptors(source, destination, notes):
    """Keep the HID ID in metadata and use portable names on the FAT boot USB."""
    descriptors = []
    destination.mkdir()
    for node in sorted(source.glob('*'), key=lambda p: p.name) if source.is_dir() else []:
        if not re.search(r':(?:0*044E:0*1218\.|0*056A:)', node.name, re.I):
            continue
        try:
            data = (node / 'report_descriptor').read_bytes()
        except OSError as error:
            notes.append(f'HID descriptor source read failed: {node.name}: {error.strerror}')
            continue
        if not data or len(data) > 65536:
            notes.append(f'HID descriptor unexpected length: {node.name}: {len(data)}')
            continue
        # A Linux HID node contains ':', which VFAT rejects with EINVAL.
        filename = re.sub(r'[^A-Za-z0-9_.-]', '_', node.name) + '.bin'
        target = destination / filename
        try:
            with target.open('xb') as output:
                output.write(data)
        except OSError as error:
            notes.append(f'HID descriptor output write failed: {node.name}: {error.strerror}')
            continue
        descriptors.append({'HIDNode': node.name, 'File': 'hid-report-descriptors/' + filename,
                            'Length': len(data), 'SHA256': hashlib.sha256(data).hexdigest()})
    return descriptors


def collect_usb_descriptors(source, destination, notes):
    """Copy kernel-cached descriptors only, with no USB requests or strings."""
    targets = {('044e','1218'), ('0bda','5671'), ('0bda','565e'),
               ('8087','0026'), ('06cb','00bc'), ('0a5c','5842'), ('413c','81e0')}
    descriptors = []
    destination.mkdir()
    for node in sorted(source.glob('*'), key=lambda p: p.name) if source.is_dir() else []:
        vid, pid = read_text(node / 'idVendor'), read_text(node / 'idProduct')
        if (vid, pid) not in targets:
            continue
        if not re.fullmatch(r'[0-9]+-[0-9.]+', node.name):
            continue
        try:
            data = (node / 'descriptors').read_bytes()
        except OSError as error:
            notes.append(f'USB descriptor source read failed: {vid}:{pid}: {error.strerror}')
            continue
        if not 18 <= len(data) <= 1_048_576 or data[:2] != b'\x12\x01':
            notes.append(f'USB descriptors invalid device header/length: {vid}:{pid}')
            continue
        filename = f'{node.name}-{vid}-{pid}.bin'
        try:
            with (destination / filename).open('xb') as output:
                output.write(data)
        except OSError as error:
            notes.append(f'USB descriptor output write failed: {vid}:{pid}: {error.strerror}')
            continue
        descriptors.append({'USBNode': node.name, 'VID': vid, 'PID': pid,
                            'CurrentConfigurationValue': read_text(node / 'bConfigurationValue'),
                            'File': 'usb-descriptors/' + filename, 'Length': len(data),
                            'SHA256': hashlib.sha256(data).hexdigest()})
    return descriptors


def decode_cml_ggc(data):
    if len(data) != 2:
        raise ValueError('GGC requires two bytes')
    raw = int.from_bytes(data, 'little')
    if raw == 0xffff:
        raise ValueError('PCI config returned all ones')
    gms, ggms = (raw >> 8) & 0xff, (raw >> 6) & 3
    # Linux gen9_stolen_size also covers INTEL_CML_IDS. 0xff is outside
    # the documented 0x00..0xfe ranges, so retain it without guessing.
    stolen_mib = gms * 32 if gms < 0xf0 else (gms - 0xf0 + 1) * 4 if gms <= 0xfe else None
    return {'RawWordHex': f'0x{raw:04x}', 'GMSHex': f'0x{gms:02x}',
            'GraphicsStolenPreallocatedMiB': stolen_mib,
            'GTTMemoryMiB': (1 << ggms) if ggms else 0,
            'Limit': 'Hardware graphics preallocation at this boot, not DVMT maximum shared memory or an IFR setup variable.'}


def decode_msr_e2(data):
    if len(data) != 8:
        raise ValueError('MSR E2 requires eight bytes')
    value = int.from_bytes(data, 'little')
    return {'RawValueHex': f'0x{value:016x}', 'CFGLockBit15': bool(value & (1 << 15))}


def collect_platform_readings(notes):
    result = {'PCIConfigWrites': False, 'MSRWrites': False, 'FirmwareVariablesWritten': False,
              'MSRModuleLoadedByCollector': False, 'MSRModuleLoadPolicy': 'Only bundled msr module, with allow_writes=off if not already loaded',
              'Sources': ['https://github.com/torvalds/linux/blob/v6.18/arch/x86/kernel/early-quirks.c',
                          'https://github.com/torvalds/linux/blob/v6.18/include/drm/intel/i915_drm.h',
                          'https://github.com/torvalds/linux/blob/v6.18/arch/x86/kernel/msr.c',
                          'https://github.com/tianocore/edk2/blob/master/MdePkg/Include/Register/Intel/Msr/SandyBridgeMsr.h']}
    gpu = Path('/sys/bus/pci/devices/0000:00:02.0')
    identity = {'Vendor': read_text(gpu / 'vendor'), 'Device': read_text(gpu / 'device')}
    graphics = {'BDF': '0000:00:02.0', **identity, 'RegisterOffset': '0x50', 'Length': 2}
    result['GraphicsPreallocation'] = graphics
    if identity != {'Vendor': '0x8086', 'Device': '0x9b41'}:
        graphics['State'] = 'NOT_READ_UNEXPECTED_GPU'
        notes.append('GGC not read: expected Intel Comet Lake 8086:9b41')
    else:
        try:
            with (gpu / 'config').open('rb', buffering=0) as stream:
                stream.seek(0x50)
                data = stream.read(2)
            graphics.update({'State': 'READ', 'BytesHex': data.hex(), **decode_cml_ggc(data)})
        except (OSError, ValueError) as error:
            graphics.update({'State': 'UNAVAILABLE', 'ErrorType': type(error).__name__})
            notes.append('GGC read unavailable: ' + type(error).__name__)
    module = Path('/sys/module/msr')
    result['MSRModuleWasAlreadyLoaded'] = module.is_dir()
    if not module.is_dir():
        modprobe = shutil.which('modprobe')
        if modprobe:
            try:
                reply = subprocess.run([modprobe, 'msr', 'allow_writes=off'], capture_output=True, timeout=20, check=False)
                result['MSRModuleLoadExitCode'] = reply.returncode
                result['MSRModuleLoadedByCollector'] = reply.returncode == 0 and module.is_dir()
            except (OSError, subprocess.TimeoutExpired) as error:
                result['MSRModuleLoadErrorType'] = type(error).__name__
        else:
            result['MSRModuleLoadErrorType'] = 'Bundled modprobe unavailable; no installation attempted'
    result['MSRAllowWritesParameter'] = read_text(module / 'parameters/allow_writes')
    cpus = []
    for node in Path('/sys/devices/system/cpu').glob('cpu[0-9]*'):
        if re.fullmatch(r'cpu[0-9]+', node.name) and (read_text(node / 'online') in (None, '1')):
            cpus.append(int(node.name[3:]))
    cpus = sorted(cpus)
    if not cpus or len(cpus) > 64:
        result['CFGStatus'] = 'UNKNOWN_INVALID_ONLINE_CPU_LIST'
        notes.append('CFG Lock not read: invalid online CPU list')
        return result
    registers = []
    for cpu in cpus:
        node = Path('/dev/cpu') / str(cpu) / 'msr'
        entry = {'CPU': cpu, 'Register': '0xe2', 'OpenMode': 'O_RDONLY'}
        registers.append(entry)
        try:
            info = node.stat()
            if not stat.S_ISCHR(info.st_mode) or os.major(info.st_rdev) != 202 or os.minor(info.st_rdev) != cpu:
                entry['State'] = 'NOT_READ_UNEXPECTED_DEVICE_NODE'
                continue
            with node.open('rb', buffering=0) as stream:
                data = os.pread(stream.fileno(), 8, 0xe2)
            entry.update({'State': 'READ', 'BytesHex': data.hex(), **decode_msr_e2(data)})
        except (OSError, ValueError) as error:
            entry.update({'State': 'UNAVAILABLE', 'ErrorType': type(error).__name__})
    result['CFGLockPerOnlineCPU'] = registers
    observed = [entry['CFGLockBit15'] for entry in registers if entry.get('State') == 'READ']
    result['CFGStatus'] = ('LOCKED' if all(observed) else 'UNLOCKED' if not any(observed) else 'MIXED') if len(observed) == len(cpus) else 'UNKNOWN_PARTIAL_OR_UNAVAILABLE'
    if len(observed) != len(cpus):
        notes.append('CFG Lock data incomplete: MSR E2 unavailable on one or more online CPUs')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', help='A NEW output directory; parent must exist')
    args = parser.parse_args()
    if sys.platform != 'linux':
        raise SystemExit('Run this collector in native Linux on the Dell, not Windows.')
    release = read_text('/proc/sys/kernel/osrelease') or ''
    if re.search(r'microsoft|wsl', release, re.I):
        raise SystemExit('WSL cannot provide the physical firmware tables; boot native Linux.')
    model = read_text('/sys/class/dmi/id/product_name')
    if model != 'Latitude 7210 2-in-1':
        raise SystemExit('Unexpected model. Run on the Latitude 7210 2-in-1 itself.')
    if os.geteuid() != 0:
        raise SystemExit('Root read access is needed for ACPI/HID/codec files; use sudo python3.')
    stamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
    destination = Path(args.output or f'hackintosh-linux-audit-{stamp}').expanduser().resolve()
    archive = destination.with_suffix('.zip')
    if destination.exists() or archive.exists() or not destination.parent.is_dir():
        raise SystemExit('Choose a new output name inside an existing parent directory.')
    destination.mkdir()
    notes = []
    result = {'CollectedAtUtc': datetime.now(timezone.utc).isoformat(),
              'KernelRelease': release, 'Model': model,
              'Method': 'Native Linux read-only sysfs/procfs inventory',
              'Privacy': 'No machine serials, machine UUIDs, MAC/IP addresses, license or recovery keys.',
              'ValidationLimit': 'Successful collection is not a macOS functionality test.'}
    dmi = {}
    for field in ('sys_vendor', 'product_name', 'board_vendor', 'board_name', 'board_version',
                  'bios_vendor', 'bios_version', 'bios_date'):
        dmi[field] = read_text('/sys/class/dmi/id/' + field)
    result['DMI'] = dmi
    cpu = read_text('/proc/cpuinfo') or ''
    result['CPU'] = sorted({line for line in cpu.splitlines()
                            if re.match(r'^(vendor_id|cpu family|model\s|model name|stepping|flags)\s*:', line)})
    acpi = []
    for subdir, source in (('static', Path('/sys/firmware/acpi/tables')),
                           ('dynamic', Path('/sys/firmware/acpi/tables/dynamic'))):
        if not source.is_dir():
            notes.append(f'ACPI directory unavailable: {subdir}')
            continue
        target = destination / 'acpi' / subdir
        target.mkdir(parents=True, exist_ok=True)
        for entry in sorted(source.iterdir()):
            if not entry.is_file() or not re.fullmatch(r'[A-Za-z0-9_]+', entry.name):
                continue
            if re.match(r'^(MSDM|SLIC|WPBT)', entry.name):
                continue
            try:
                data = entry.read_bytes()
            except OSError as error:
                notes.append(f'ACPI read failed: {entry.name}: {error.strerror}')
                continue
            signature = data[:4].decode('ascii', errors='replace')
            if signature in ('MSDM', 'SLIC', 'WPBT'):
                continue
            file = target / (entry.name + '.dat')
            file.write_bytes(data)
            standard = signature != 'FACS' and len(data) >= 36
            acpi.append({'File': file.relative_to(destination).as_posix(),
                         'Signature': signature, 'Length': len(data),
                         'HeaderLength': struct.unpack_from('<I', data, 4)[0] if len(data) >= 8 else None,
                         'ChecksumApplicable': standard,
                         'ChecksumValid': sum(data) % 256 == 0 if standard else None,
                         'SHA256': hashlib.sha256(data).hexdigest()})
    result['ACPITables'] = acpi
    result['UniqueSSDTCount'] = len({t['SHA256'] for t in acpi if t['Signature'] == 'SSDT'})
    result['SSDTCoverageNote'] = 'Compare the actual exported tables with the Windows count of eight; collection alone does not prove coverage.'
    codec_dir = destination / 'audio-codecs'
    codec_dir.mkdir()
    for name in sorted(glob.glob('/proc/asound/card*/codec#*')):
        source = Path(name)
        try:
            (codec_dir / f'{source.parent.name}-{source.name}.txt').write_bytes(source.read_bytes())
        except OSError as error:
            notes.append(f'Audio codec read failed: {source.name}: {error.strerror}')
    result['HIDReportDescriptors'] = collect_hid_descriptors(
        Path('/sys/bus/hid/devices'), destination / 'hid-report-descriptors', notes)
    result['USBDescriptors'] = collect_usb_descriptors(
        Path('/sys/bus/usb/devices'), destination / 'usb-descriptors', notes)
    result['PlatformReadings'] = collect_platform_readings(notes)
    result['IIOSensors'] = [{'Name': read_text(node / 'name'),
                             'ChannelNames': sorted(p.name for p in node.glob('in_*'))}
                            for node in Path('/sys/bus/iio/devices').glob('iio:device*')]
    result['NVMe'] = [{'Model': read_text(node / 'model'), 'Firmware': read_text(node / 'firmware_rev')}
                      for node in Path('/sys/class/nvme').glob('nvme*')]
    commands = {
        'pci-devices.txt': ['lspci', '-nnk'],
        'usb-devices.txt': ['lsusb'],
        'usb-tree.txt': ['lsusb', '-t'],
        'block-devices.txt': ['lsblk', '-o', 'NAME,TYPE,SIZE,MODEL,TRAN,LOG-SEC,PHY-SEC'],
        'audio-playback-devices.txt': ['aplay', '-l'],
        'audio-capture-devices.txt': ['arecord', '-l'],
    }
    for name, command in commands.items():
        if not shutil.which(command[0]):
            notes.append(f'Command not installed; skipped without installing: {command[0]}')
            continue
        try:
            completed = subprocess.run(command, capture_output=True, text=True, timeout=30, check=False)
            (destination / name).write_text(completed.stdout + completed.stderr, encoding='utf-8')
        except (OSError, subprocess.TimeoutExpired) as error:
            notes.append(f'Command failed: {command[0]}: {type(error).__name__}')
    result['Notes'] = notes
    (destination / 'linux-inventory.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    checksums = []
    for file in sorted(destination.rglob('*')):
        if file.is_file():
            checksums.append(hashlib.sha256(file.read_bytes()).hexdigest() + '  ' + file.relative_to(destination).as_posix())
    (destination / 'SHA256SUMS.txt').write_text('\n'.join(checksums) + '\n', encoding='utf-8')
    with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED) as output:
        for file in sorted(destination.rglob('*')):
            if file.is_file():
                output.write(file, destination.name + '/' + file.relative_to(destination).as_posix())
    print(json.dumps({'Output': str(destination), 'ZIP': str(archive),
                      'ACPITables': len(acpi), 'UniqueSSDT': result['UniqueSSDTCount'],
                      'MacOSVerified': False, 'Notes': notes}, indent=2))


if __name__ == '__main__':
    main()
