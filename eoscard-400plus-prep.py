import argparse
import os
import sys

FAT16_EOS_OFFSET = 43
FAT16_BOOT_OFFSET = 64
FAT32_EOS_OFFSET = 71
FAT32_BOOT_OFFSET = 92

EOS = b"EOS_DEVELOP"
BOOT = b"BOOTDISK"


def read_sector(path):
    with open(path, 'rb') as f:
        return f.read(512)


def detect_fat_type(sector):
    if len(sector) < 512:
        raise ValueError('Could not read boot sector (need 512 bytes).')
    fs16 = sector[54:62].rstrip(b' \x00')
    fs32 = sector[82:90].rstrip(b' \x00')
    if fs16 in (b'FAT12', b'FAT16'):
        return fs16.decode('ascii')
    if fs32 == b'FAT32':
        return 'FAT32'
    return None


def offsets_for(fs_type):
    if fs_type in ('FAT12', 'FAT16'):
        return FAT16_EOS_OFFSET, FAT16_BOOT_OFFSET
    if fs_type == 'FAT32':
        return FAT32_EOS_OFFSET, FAT32_BOOT_OFFSET
    raise ValueError('Unsupported filesystem; expected FAT12/FAT16/FAT32.')


def verify_flags(sector, eos_off, boot_off):
    return sector[eos_off:eos_off+11] == EOS and sector[boot_off:boot_off+8] == BOOT


def existing_volume_label(sector, fs_type):
    off = FAT16_EOS_OFFSET if fs_type in ('FAT12', 'FAT16') else FAT32_EOS_OFFSET
    return sector[off:off+11]


def device_size_bytes(path):
    """Return device size in bytes, or None if it can't be determined.

    On Windows, seek-to-end on a raw volume handle works for the volume's size.
    """
    try:
        with open(path, 'rb') as f:
            f.seek(0, os.SEEK_END)
            size = f.tell()
            return size if size > 0 else None
    except OSError:
        return None


def human_bytes(n):
    if n is None:
        return 'unknown'
    for unit in ('B', 'KB', 'MB', 'GB', 'TB'):
        if n < 1024:
            return f'{n:.1f} {unit}'
        n /= 1024
    return f'{n:.1f} PB'


def confirm(prompt):
    try:
        ans = input(prompt).strip().lower()
    except EOFError:
        return False
    return ans in ('y', 'yes')


def write_flags(path, fs_type):
    eos_off, boot_off = offsets_for(fs_type)
    with open(path, 'r+b') as f:
        sector = bytearray(f.read(512))
        if len(sector) < 512:
            raise OSError('Could not read full 512-byte boot sector.')
        sector[eos_off:eos_off+len(EOS)] = EOS
        sector[boot_off:boot_off+len(BOOT)] = BOOT
        f.seek(0)
        f.write(bytes(sector))
        f.flush()
        os.fsync(f.fileno())
    sector = read_sector(path)
    return verify_flags(sector, eos_off, boot_off)


def main():
    ap = argparse.ArgumentParser(
        description='Set EOS_DEVELOP and BOOTDISK on a FAT/FAT32 card for Canon 400plus.'
    )
    ap.add_argument(
        'device',
        help=r'Windows volume or physical drive path, e.g. \\.\E: or \\.\PhysicalDrive2'
    )
    ap.add_argument(
        '--check',
        action='store_true',
        help='Only verify flags, do not modify the card'
    )
    ap.add_argument(
        '--force',
        action='store_true',
        help='Skip the interactive confirmation prompt before writing'
    )
    args = ap.parse_args()

    device = args.device
    try:
        sector = read_sector(device)
    except PermissionError:
        print('ERROR: Permission denied. Run Command Prompt or PowerShell as Administrator.', file=sys.stderr)
        sys.exit(2)
    except FileNotFoundError:
        print(f'ERROR: Device not found: {device}', file=sys.stderr)
        sys.exit(2)
    except OSError as e:
        print(f'ERROR: Could not open {device}: {e}', file=sys.stderr)
        sys.exit(2)

    fs_type = detect_fat_type(sector)
    if not fs_type:
        print('ERROR: Could not detect FAT12/FAT16/FAT32 from the first sector. Format the card in-camera first.', file=sys.stderr)
        sys.exit(3)

    eos_off, boot_off = offsets_for(fs_type)
    already = verify_flags(sector, eos_off, boot_off)
    label = existing_volume_label(sector, fs_type).rstrip(b' \x00').decode('ascii', errors='replace')
    size = device_size_bytes(device)

    print(f'Device:      {device}')
    print(f'Size:        {human_bytes(size)}')
    print(f'Filesystem:  {fs_type}')
    print(f'Volume label: {label!r}')
    print(f'EOS_DEVELOP: {"present" if sector[eos_off:eos_off+11] == EOS else "missing"}')
    print(f'BOOTDISK:    {"present" if sector[boot_off:boot_off+8] == BOOT else "missing"}')

    if args.check:
        sys.exit(0 if already else 1)

    if already:
        print('Both flags are already present. No changes made.')
        sys.exit(0)

    if size is not None and size > 64 * 1024 * 1024 * 1024:
        print(f'ERROR: Device is {human_bytes(size)} — larger than any plausible 400D CF card.', file=sys.stderr)
        print('Refusing to write. Use --force only if you are certain this is the right device.', file=sys.stderr)
        if not args.force:
            sys.exit(5)

    if not args.force:
        print()
        print('About to write EOS_DEVELOP and BOOTDISK to the boot sector of the device above.')
        print('This will overwrite bytes in the FAT boot sector. Verify the device path is correct.')
        if not confirm('Type "yes" to proceed: '):
            print('Aborted.')
            sys.exit(0)

    ok = write_flags(device, fs_type)
    if not ok:
        print('ERROR: Write attempt completed but verification failed.', file=sys.stderr)
        sys.exit(4)

    print('Successfully wrote EOS_DEVELOP and BOOTDISK.')
    print('Next, manually copy AUTOEXEC.BIN and the 400PLUS folder to the card root.')


if __name__ == '__main__':
    main()
