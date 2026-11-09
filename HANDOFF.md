# Handoff: changes made on 2026-11-08

Everything that was changed on the Kindle and on the Mac during this session, the current state, and how to undo each item. For the "why" and the errors along the way, see [docs/troubleshooting.md](docs/troubleshooting.md).

## Current state

| | |
|---|---|
| Cover (hall) sensor | **Disabled**, and stays disabled across reboots |
| USBNetwork | Installed (0.22.N), KUAL toggle working, **not** auto-start, Wi-Fi SSH **off** |
| Kindle drive (FAT32) | Repaired with `diskutil repairVolume`; Spotlight indexing turned off (`mdutil -i off`) |
| OTA updates | Still blocked by the existing `renameotabin` extension (unchanged) |

## Changes on the Kindle

### System partition (read-only root, remounted briefly with `mntroot rw`)

| Path | Change | Undo |
|---|---|---|
| `/etc/upstart/disable-hall.conf` | **Added.** Upstart task; after `powerd` starts, waits 5 s and writes `0` to `hall_enable`. Skips itself if `/mnt/us/ENABLE_HALL` exists. Copy in [hall-sensor/disable-hall.conf](hall-sensor/disable-hall.conf). | `scripts/uninstall-hall-disable.sh`, or create `ENABLE_HALL` at the drive root and reboot |

Root was put back to read-only afterwards (verified: `/dev/root on / type ext3 (ro,...)`).

### Runtime (not persistent on its own)

| Setting | Before | After |
|---|---|---|
| `/sys/devices/system/wario_hall/wario_hall0/hall_enable` | `1` | `0` (re-applied at every boot by the job above) |

### Kindle drive (`/mnt/us`, the USB-visible storage)

| Path | Change |
|---|---|
| `usbnet/` | **Added** by the USBNetwork MR package (binaries, `etc/config`, host keys). Config left at defaults: `KINDLE_IP=192.168.15.244`, `USE_WIFI="false"`, `DISABLED_auto` (not auto-start). |
| `extensions/usbnet/` | **Added** by the reinstall (KUAL menu / toggle). The first attempt hit an I/O error and left an empty folder; after the disk repair the package was reinstalled successfully. |
| `extensions/MRInstaller/log/mrinstaller.log` | Appended by MRPI (install history; useful for debugging). |
| `mrpackages/` | MRPI consumed `Update_usbnet_0.22.N_install_pw2_and_up.bin` and a KUAL Booklet `.bin` (KUAL Booklet was reinstalled as a side effect — harmless). |
| `.Trashes/501/` | **Deleted** (macOS trash on the Kindle, held an old copy of USBNetwork with corrupt entries). |
| `._*` files | **Deleted** (macOS AppleDouble files; MRPI can trip on them). |
| `.metadata_never_index` | **Added** so Spotlight never indexes the Kindle again. |
| Filesystem | `diskutil repairVolume` fixed corrupt entries (bad long-filename entry under `.Spotlight-V100`, `.fseventsd` with no clusters). `FSCK0000.REN` in `mrpackages/` was a leftover from an earlier disk check. |

Nothing in `documents/`, `koreader/`, `linkss/`, or the jailbreak files was touched.

## Changes on the Mac

| Item | Change | Undo |
|---|---|---|
| Network: "RNDIS/Ethernet Gadget" (`en7`) | Set to manual `192.168.15.201 / 255.255.255.0` (was DHCP → `169.254.x.x`). Only affects the Kindle's USB adapter. | System Settings → Network → RNDIS/Ethernet Gadget → DHCP, or `networksetup -setdhcp "RNDIS/Ethernet Gadget"` |
| Spotlight on `/Volumes/Kindle` | `sudo mdutil -i off` | `sudo mdutil -i on /Volumes/Kindle` |
| `~/.kindle-ssh/id_ed25519{,.pub}` | **Added** an SSH key for the Kindle (not installed on it; not needed). | `rm -rf ~/.kindle-ssh` |
| `/tmp/kindle_known_hosts` | Kindle host key cached during the session (temporary). | none needed |
| This repo | `~/Documents/GitHub/kindle-pw3-mods` | — |

## How to verify

```sh
./scripts/mac-usbnet-setup.sh
./scripts/kssh.sh 'cat /sys/devices/system/wario_hall/wario_hall0/hall_enable; ls -l /etc/upstart/disable-hall.conf'
# expect: 0 and the file listed
```

After a real reboot, close the case or hold a magnet to it: the Kindle should stay awake.

## Known risks / follow-ups

- **Firmware update** removes `/etc/upstart/disable-hall.conf` (re-run `scripts/install-hall-disable.sh` if the jailbreak survives). Keep OTA blocked.
- **SSH over USB accepts any password.** Don't enable `USE_WIFI` without setting a root password or installing `~/.kindle-ssh/id_ed25519.pub` into `usbnet/etc/authorized_keys`.
- **The FAT32 drive got corrupted before**, most likely from unplugging without ejecting and from Spotlight writes. Always eject (`scripts/prep-kindle-drive.sh`).
- Not yet done: a real reboot test (the job was tested by running it by hand).
