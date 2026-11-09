# Kindle PW3 Etch A Sketch Calendar

Notes, scripts and config for my jailbroken **Kindle Paperwhite 3 (7th gen, 2015)**, mainly:

- **Permanently disabling the magnetic cover (hall) sensor** in software
- Installing **USBNetwork** and getting **SSH over USB** working from a Mac
- Repairing the Kindle's FAT32 storage when installs fail
- How the work was done with **Claude** driving the Mac (and the Kindle over SSH)

**Start with [HANDOFF.md](HANDOFF.md)** — a complete list of every change made to the Kindle and the Mac, and how to undo each one.

## Device

| | |
|---|---|
| Model | Kindle Paperwhite 3 (7th generation, 2015) — *not* PW1 (2012) or PW2 (2013) |
| Firmware | 5.16.2.1.1 |
| Kernel | Linux 3.0.35-lab126 (armv7l), "wario" platform |
| Jailbreak | WinterBreak (Mesquito) + hotfix |
| Installed | KUAL, MRPI (MRInstaller), KOReader, linkss, onlinescreensaver, renameotabin (OTA blocker), python/python3, USBNetwork 0.22.N |

## Layout

```
HANDOFF.md                  Every change made, current state, how to undo
hall-sensor/
  disable-hall.conf         Upstart job installed to /etc/upstart/ on the Kindle
  README.md                 How the sensor works, the sysfs knobs, install/undo
scripts/
  kssh.sh                   Non-interactive SSH helper (Mac -> Kindle over USB)
  mac-usbnet-setup.sh       Give the Mac 192.168.15.201 on the Kindle's RNDIS adapter
  install-hall-disable.sh   Push + activate the Upstart job from the Mac
  uninstall-hall-disable.sh Remove it and re-enable the sensor
  prep-kindle-drive.sh      Pre-eject cleanup: Spotlight off, ._ files, verify/repair
docs/
  usbnetwork.md             Installing USBNetwork via MRPI and connecting over SSH
  troubleshooting.md        Every error hit along the way and its fix
  claude-workflow.md        How Claude was connected and what it did
```

## Quick start

With the Kindle plugged in and USBNetwork toggled **on** (KUAL → USBNetwork):

```sh
./scripts/mac-usbnet-setup.sh          # Mac side: 192.168.15.201
./scripts/kssh.sh 'cat /sys/devices/system/wario_hall/wario_hall0/hall_enable'
./scripts/install-hall-disable.sh      # make the change permanent
```

Undo: create an empty file `ENABLE_HALL` at the root of the Kindle drive and reboot, or run `./scripts/uninstall-hall-disable.sh`.

## Caveats

- A firmware update wipes `/etc/upstart/disable-hall.conf` (and may remove the jailbreak). Keep OTA blocked with `renameotabin`.
- The USBNetwork SSH server (dropbear, default config) accepted **any password over USB**. Fine on a cable; do **not** set `USE_WIFI="true"` in `usbnet/etc/config` without setting a real root password or keys first.
- Everything here is done at your own risk.
