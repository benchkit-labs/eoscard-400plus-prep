# 400plus CF Card Prep Utility

A small Python utility for Windows that writes the two Canon boot flags required for a [400plus](https://github.com/400plus/400plus) boot card on a Canon EOS 400D / Digital Rebel XTi.

The flags it writes:

- `EOS_DEVELOP`
- `BOOTDISK`

It does **not** copy `AUTOEXEC.BIN` or the optional `400PLUS` folder — you still copy those by hand from the official 400plus release archive.

## ⚠️ Disclaimer — read before using

**What this script does:**

This utility writes a small number of bytes directly to the **first 512-byte sector (the FAT boot sector) of a CompactFlash card** that you specify by raw device path (e.g. `\\.\E:` on Windows). Specifically, it patches two short ASCII strings (`EOS_DEVELOP` and `BOOTDISK`) at documented offsets inside that sector. It does not touch the rest of the card, it does not write anywhere else on your system, and it does not modify your camera in any way.

**What can go wrong:**

- **You target the wrong device.** Raw device paths look almost identical to each other. If you type `\\.\PhysicalDrive0` instead of the path to your CF card, you will overwrite the boot sector of whatever drive that turns out to be — potentially including the system disk you booted from. The script tries to protect you (it refuses devices larger than 64 GB without `--force`, and prompts for `yes` confirmation showing the device path and size) but the final responsibility for picking the right device is yours.
- **Data loss on the targeted card.** Even on the correct CF card, modifying the FAT boot sector can render the card temporarily unreadable to Windows in rare cases. The fix is to reformat the card in the camera — but anything that was on the card is gone.
- **Brick risk on the camera if you confuse `.FIR` files with this script.** This script does **not** flash camera firmware. But the 400plus install process exists in the same world as Canon's `.FIR` firmware-update mechanism, and it is easy to confuse the two. Loading a tampered or wrong-model `.FIR` file via the camera's MENU → Firmware Ver. → SET flow **can permanently brick the camera**. Read the troubleshooting section about `.FIR` files carefully and do not load `.FIR` files from third-party sources.
- **The 400plus firmware hack itself carries some risk.** 400plus is a third-party project that is not affiliated with Canon. It loads into the camera's RAM from the card each power-on and is removed when the card is removed, so the risk profile is much lower than a permanent firmware flash — but you are still running unofficial code on your camera. If something goes wrong, Canon will not support you.
- **This tool is provided as-is, with no warranty.** It was developed and tested against one specific Canon EOS 400D / Rebel XTi body with one specific SanDisk Ultra II 2 GB CF card. Your hardware may behave differently. The author and contributors are not responsible for any damage to your camera, your CF cards, your computer, or any data on any of the above.

**By using this script, you acknowledge that:**

1. You understand it writes directly to a raw disk device and that selecting the wrong device path will overwrite the first sector of whatever device you point it at.
2. You are running it on hardware (camera, CF card, computer) that you own and accept responsibility for.
3. You have read the safety prompts in the script's output and will verify the device summary it prints before typing `yes`.
4. You accept that 400plus is an unofficial firmware modification and that any decision to install it on your camera is yours alone.
5. **You will run `--check` (read-only, safe) first** to confirm the script can see your card and identifies it correctly, before running the write path.

If any of that gives you pause: stop, don't run the script, and consider whether 400plus is something you actually need on this camera.

## Why this exists

The standard tool ([EOScard](http://chdk.wikia.com/wiki/EOScard)) refuses to set both `BOOTDISK` and `EOS_DEVELOP` together unless you supply Canon firmware `MF` files. With `BOOTDISK` alone, 400plus will not load. This utility writes both flags directly, no MF files required.

## Safety

- Run it as **Administrator** on Windows (raw volume access requires it).
- Use it only on the CF card you intend to prep — the script will refuse anything larger than 64 GB unless you pass `--force`.
- The script prompts for `yes` confirmation before writing. Read the device summary it prints first.
- Format the CF card in the camera before running this.
- Close any Explorer windows that may be touching the card.

## Requirements

- Windows 10 / 11
- Python 3.8 or newer (no third-party packages needed)
- A USB CF card reader
- An EOS 400D / Digital Rebel XTi on Canon firmware **1.1.1**

### Checking your camera's firmware

On the camera: **MENU** → rightmost yellow wrench tab → scroll to the bottom → **Firmware Ver.**

Most XTi bodies are already on `1.1.1`, since it was the last update Canon released for this body and was widely distributed. If yours shows `1.0.x`, you will need to update before 400plus can run.

### Getting Canon's 1.1.1 firmware file

Canon no longer hosts the 400D firmware on their public download pages. Do **not** install firmware from random archive sites or torrents — a malformed `.FIR` file will brick the camera. Legitimate routes:

- **Call Canon USA directly:** 1-800-OK-CANON (1-800-652-2666). Ask for the EOS Digital Rebel XTi 1.1.1 firmware. They have historically emailed the file on request.
- **Canon Community forum:** https://community.usa.canon.com — active threads exist where users walk through getting the file via official channels.

This project does not redistribute Canon firmware.

## Usage

Open **PowerShell** or **Command Prompt as Administrator**, then:

### Check (read-only, safe)

```powershell
python eoscard-400plus-prep.py \\.\E: --check
```

Replace `E:` with whatever drive letter Windows assigned to the CF card.

The check tells you the filesystem type, the current volume label, and whether each flag is present.

### Write

```powershell
python eoscard-400plus-prep.py \\.\E:
```

You will see a device summary and a `yes` prompt before any bytes are written.

### Skip the prompt (scripted use)

```powershell
python eoscard-400plus-prep.py \\.\E: --force
```

### Physical drive path (alternative)

```powershell
python eoscard-400plus-prep.py \\.\PhysicalDrive2
```

## After the script succeeds

Download the latest 400plus release zip:

- https://github.com/400plus/400plus/releases

Inside the zip, the `bin\` folder contains `AUTOEXEC.BIN` and `languages.ini`. Copy them onto the card:

```text
E:\
├─ AUTOEXEC.BIN
└─ 400PLUS\
   └─ LANGUAGES.INI   (optional, only if you want non-English languages)
```

`AUTOEXEC.BIN` at the root is the only required file. The `400PLUS\LANGUAGES.INI` is optional.

Safely eject the card from Windows, then put it in the camera.

## How do I know it worked?

This is the part the wiki does not make obvious for the XTi: **there is no boot splash on the LCD.** The XTi has no separate blue indicator LED the way some other Canon bodies do.

What you should see:

- When you **insert the card and close the door** with the camera off, the **red** card-access LED flashes (camera reading the card) and then the **Direct Print** button (top-left back of the camera, the one with the blue printer icon and squiggly arrow) **briefly flashes blue**. That blue flash is 400plus saying "I loaded."
- After turning the camera on, with the shooting info screen visible, press the **Direct Print** button. The 400plus menu appears on the LCD.
- Exit the 400plus menu by half-pressing the shutter.

If the Direct Print button does not flash blue on card insert, 400plus is not loading. See troubleshooting below.

## Troubleshooting

### "It doesn't work — nothing happens when I turn the camera on"

This is the single most common report, and **the most common cause is that 400plus is actually loading fine, but the XTi gives you no visible confirmation on the LCD.** There is no boot splash on this camera body. Before assuming the install failed, do this:

1. Power the camera **off**.
2. Open the card door, remove the card, then reinsert it and close the door — **while the camera is still off**.
3. Watch the **Direct Print** button (top-left back of the camera, marked with a blue printer icon and a squiggly arrow line).
4. You should see the **red** card-access LED flash briefly (camera reading the card), followed by the Direct Print button **briefly flashing blue**.

That blue flash is 400plus saying "I loaded." If you see it, you are done — 400plus is running. Press the Direct Print button from the shooting info screen at any time to open the 400plus menu.

If you don't see the blue flash, work through the checks below.

### Checks if the blue Direct Print flash does not appear

1. **Verify the boot flags survived.** Put the card in your PC and run `python eoscard-400plus-prep.py \\.\<drive> --check`. Both flags should report `present`. The camera does not wipe them on its own, but **re-formatting the card in the camera will**.
2. **Confirm firmware 1.1.1.** MENU → rightmost yellow wrench tab → bottom → Firmware Ver. If it says `1.0.x`, the camera must be updated to 1.1.1 first (see "Getting Canon's 1.1.1 firmware file" above).
3. **Verify `AUTOEXEC.BIN` is at the card root** (not inside a `bin\` subfolder) and is the genuine file. SHA-256 of the official `20160404-10` build is:
   ```
   8b7fdaf6026a93419f2e56847d3c69beacd944f6a5e1f8bab2e9d395f4702963
   ```
   In PowerShell: `Get-FileHash <drive>:\AUTOEXEC.BIN -Algorithm SHA256`.
4. **Remove any stray `.FIR` files from the card root.** Canon's firmware-update scanner runs early in the boot path, and an unrecognized `.FIR` can interfere with the bootloader. The card only needs `AUTOEXEC.BIN` (and optionally `400PLUS\LANGUAGES.INI`) — nothing else.
5. **Try a smaller, older CF card.** 400plus was developed in the 512 MB – 4 GB era. Modern high-speed or large-capacity CF cards sometimes do not boot it. Classic SanDisk Ultra II 1-2 GB cards are known good.
6. **Fully charge the battery.** The bootloader has been reported to misbehave with low batteries, even when the camera otherwise operates normally.
7. **Cold-boot the camera.** Remove the battery (or both batteries from the BG-E3 grip) for 30 seconds, reinsert, then try again. Some boot-state issues only clear with a full power drain.

### Gotchas worth flagging

**EOScard refuses to set both flags without firmware MF files.**
That is why this tool exists. EOScard will let you set `BOOTDISK` alone but not `EOS_DEVELOP` without supplying Canon's MF firmware files (which most people do not have). With only `BOOTDISK`, 400plus will not load. This script writes both directly.

**Do not reformat the card in the camera after running this script.**
Camera formatting wipes the FAT boot sector, removing both flags. If you do format, just re-run this script to put them back.

**The script needs Administrator and exclusive access to the card.**
Close Explorer windows showing the card before running. If you get `[Errno 13] Permission denied`, run the terminal as Administrator. If you get `[Errno 22] Invalid argument`, an Explorer window or background indexer is probably holding the volume — close them and retry.

**A `.FIR` file on the card is not the same as installing 400plus.**
The `.FIR` path uses Canon's MENU → Firmware Ver. → SET flow, which actually writes to camera ROM (risk of bricking with a bad file). 400plus uses the bootloader-from-card path, which loads into RAM each power-on and never modifies the camera. Keep them straight. **This project only uses the bootloader path. It does not touch camera firmware.**

**Camera hangs with the green LED stuck on after putting a `.FIR` on the card.**
You have triggered Canon's firmware-update routine with a file it cannot process. Pull the battery (this is the documented recovery path — the firmware-update mechanism is designed to be interruptible), wait 30 seconds, reinsert, power on without the card. The camera will recover. **Then never load a `.FIR` from a third-party source again** — that is how cameras get bricked.

**400plus reset to factory defaults? Settings not persisting?**
400plus stores its settings on the card. If you swap cards, you start fresh on each one. Consider that a feature for testing prep, an annoyance for daily use — keep one "good" card and prep others only when needed.

### What "working" looks like

Once 400plus is loaded:

- The **Direct Print** button from the shooting info screen opens the 400plus menu on the LCD.
- The 400plus menu has tabs for shortcuts, expanded ISO (H1/H2 = 3200/6400 unlocked), bracketing (up to 7 frames), intervalometer, custom timer, mirror lockup behavior, and various 40D-style features.
- Half-pressing the shutter exits the 400plus menu and returns to shooting.
- 400plus is loaded fresh on every card insert — there is nothing persistent in the camera. Eject the card properly, swap to a non-prepped card, and the camera behaves as stock again.

## How it works

The 400plus wiki specifies two strings the camera's bootloader looks for in the volume's first sector (the FAT boot sector / BPB):

For **FAT12 / FAT16** cards:

- `EOS_DEVELOP` at byte offset 43 (the volume-label field)
- `BOOTDISK` at byte offset 64 (overwriting the filesystem-type field)

For **FAT32** cards:

- `EOS_DEVELOP` at byte offset 71
- `BOOTDISK` at byte offset 92

The script reads the full 512-byte sector, patches those two strings in memory, and writes the whole sector back in one aligned write (Windows requires sector-aligned I/O on raw volume handles, so byte-level seeks would fail with `EINVAL`).

## References

- 400plus project: https://github.com/400plus/400plus
- Installation wiki: https://github.com/400plus/400plus/wiki/Firmware-Hack-Installation
- User guide (menu): https://github.com/400plus/400plus/wiki/User-Guide:-The-Menu
- Releases: https://github.com/400plus/400plus/releases

## Not on Windows? Use this prompt with any AI assistant

This script is Windows-specific (it uses Windows raw volume paths like `\\.\E:`). If you are on macOS, Linux, or a different setup, you can hand the prompt below to any capable AI coding assistant (Claude, ChatGPT, Gemini, Copilot, etc.) and it should produce an equivalent utility tailored to your environment. Always read the generated code before running it as root/Administrator on a disk device.

<details>
<summary>Click to expand the prompt</summary>

````
I need a small command-line utility that prepares a CompactFlash card to boot the
400plus firmware hack on a Canon EOS 400D / Digital Rebel XTi. Please write it in
[INSERT YOUR PREFERRED LANGUAGE — e.g. Python, Bash, PowerShell, Go] for
[INSERT YOUR OS — e.g. macOS, Linux (Ubuntu), Windows].

## Background — why this utility is needed

The standard tool for this job is EOScard (an old Windows app). EOScard refuses to
set both required boot markers on a card unless the user supplies Canon firmware
"MF" files that most users do not have. With only one of the two markers set,
400plus will not load on the camera. This utility writes both markers directly to
the card's FAT boot sector, no MF files required.

It does NOT copy AUTOEXEC.BIN or the 400PLUS folder — the user copies those
manually from the official 400plus release archive after running this utility.

## What to write into the card's boot sector

The 400plus wiki (https://github.com/400plus/400plus/wiki/Firmware-Hack-Installation)
specifies that the Canon bootloader looks for two ASCII strings in the volume's
first 512-byte sector (the FAT boot sector / BPB):

For FAT12 / FAT16 cards (typically <= 2 GB):
  - "EOS_DEVELOP" (11 bytes) at byte offset 43  (overlays the BPB volume-label field)
  - "BOOTDISK"    (8 bytes)  at byte offset 64  (overlays the BPB filesystem-type field)

For FAT32 cards (typically >= 4 GB):
  - "EOS_DEVELOP" (11 bytes) at byte offset 71
  - "BOOTDISK"    (8 bytes)  at byte offset 92

These are byte offsets within the first 512-byte sector of the FAT partition
(not the MBR / not the whole disk). The script must detect FAT12/FAT16 vs FAT32
by reading the standard filesystem-type strings at sector offsets 54..62 (FAT16
field) and 82..90 (FAT32 field) before deciding which offset pair to use.

## Required behavior

1. Accept a single argument: the path to the CF card's partition / volume device.
   - On Linux: typically /dev/sdX1 or /dev/mmcblkXp1 (the first partition, not the whole disk)
   - On macOS: typically /dev/disk2s1 (use `diskutil list` to identify)
   - On Windows: \\.\E: (the volume) or \\.\PhysicalDriveN (the whole disk)
2. Read the first 512 bytes of that device. Detect FAT12/FAT16/FAT32. If neither
   is detected, abort with a clear error telling the user to format the card in
   the camera first.
3. Print a summary BEFORE writing: device path, device size in bytes (human-
   readable), filesystem type, current volume label (decoded from the BPB),
   and whether each of the two markers is already present.
4. Provide a `--check` flag that prints the summary and exits without writing
   anything. Exit 0 if both markers are present, 1 if either is missing.
5. Before writing, refuse to proceed if the device is larger than ~64 GB unless
   the user passes `--force`. (CF cards for the 400D are essentially never that
   large, so a >64 GB device is almost certainly the wrong target — typically a
   system disk picked by mistake.)
6. Before writing, prompt the user interactively to type "yes" to confirm. A
   `--force` flag should skip this prompt for scripted use.
7. Use sector-aligned I/O for the write. Raw device handles on most operating
   systems require reads and writes to be aligned to the sector size (512 bytes)
   — unaligned byte-level seek+write will fail with EINVAL / "Invalid argument"
   on Windows and may corrupt the sector on Linux/macOS. Specifically: read the
   full 512-byte sector into a buffer, patch the two marker strings in memory,
   then write the entire buffer back in a single aligned operation. Flush and
   fsync before closing.
8. After writing, re-read the sector and verify both markers are present at the
   correct offsets. If verification fails, exit with a non-zero code and a
   clear error message.

## Platform-specific notes to address in the code

- Detect when the script is not running with sufficient privileges (root on
  Unix, Administrator on Windows) and print a clear "re-run as root" /
  "re-run elevated" message rather than a generic permission error.
- On macOS, the volume must be unmounted before raw writes will succeed
  (`diskutil unmountDisk /dev/diskN`). Detect mount state and either unmount
  automatically or tell the user what to run.
- On Linux, warn if the partition appears mounted (`/proc/mounts` check) and
  refuse to write until it is unmounted.
- On Windows, the script should not require unmounting the volume, but a
  FSCTL_LOCK_VOLUME via DeviceIoControl is the proper way to prevent
  concurrent writes from Explorer/indexers if you want to be thorough.

## Safety checklist for the generated code

- Never operate on the whole disk if the user passed a partition (and vice
  versa) — accept the path as given but include the path verbatim in the
  confirmation prompt so the user sees exactly what is being written to.
- Never write outside the first 512 bytes of the target device.
- Never modify any byte except those occupied by the two marker strings.
- The two marker strings are exact ASCII, no null terminator, no padding,
  no trailing newline. Use literal byte values:
    EOS_DEVELOP = bytes [0x45, 0x4F, 0x53, 0x5F, 0x44, 0x45, 0x56, 0x45, 0x4C, 0x4F, 0x50]
    BOOTDISK    = bytes [0x42, 0x4F, 0x4F, 0x54, 0x44, 0x49, 0x53, 0x4B]

## Reference implementation (Windows / Python) for comparison

A working reference implementation in Python for Windows is at:
https://github.com/benchkit-labs/eoscard-400plus-prep
The byte offsets, marker strings, and safety pattern there have been verified
against a real Canon 400D. Use it as a sanity check for the generated code.

## What to deliver

- A single source file with the utility.
- A short README section explaining how the user identifies their CF card
  device path on their OS, runs the check, and runs the write.
- A note that after the script succeeds, the user must download the latest
  400plus release from https://github.com/400plus/400plus/releases and
  copy AUTOEXEC.BIN from its `bin/` folder to the root of the CF card.
````

</details>

After the generated script writes the boot flags, the rest of the install (copying `AUTOEXEC.BIN`, putting the card in the camera, watching for the blue Direct Print LED flash on card insert) is identical regardless of which OS prepared the card. The "How do I know it worked?" and Troubleshooting sections above apply universally.

## About this project

I am a moderately technical user who pulled an old Canon Rebel XTi off the shelf, hit the EOScard "you must supply MF files" wall, and went looking for a way around it. I wrote this utility in collaboration with **Claude Opus 4.7** (Anthropic's coding assistant) — Claude drafted the initial script, helped me debug the Windows raw-volume I/O alignment issue, walked through the byte-level boot-sector verification, and helped capture the install gotchas in this README based on what actually happened during my own first install on a real XTi.

If you are reviewing the code before running it as Administrator on a card (which you should), know that every line has been read and tested by a human against a real camera. But it is still a small script working with raw disk I/O — `--check` is read-only and safe to run first, and the write path prompts for `yes` confirmation before touching anything.

## License

MIT — see [LICENSE](LICENSE). Free to use, modify, and distribute. The "as-is, no warranty" disclaimers above are also reflected in the MIT warranty clause.

---

Part of [BenchKit Labs](https://benchkit-labs.dev) · [github.com/benchkit-labs](https://github.com/benchkit-labs)

