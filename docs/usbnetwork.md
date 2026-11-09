# USBNetwork and SSH over USB

## Which package

- PW3 = "wario" platform → **`Update_usbnet_0.22.N_install_pw2_and_up.bin`** from NiLuJe's *Snapshots* thread on MobileRead. (The Touch/PW1 build is for 2012-era devices.)
- Alternative: Marek's **USBNetLite** (KUAL-only, default login `root` / `kindle`).
- No need to re-jailbreak with WinterBreak2 first: an existing jailbreak is enough. WinterBreak2 is an initial-jailbreak method for firmware < 5.16.4.

## Install via MRPI

1. Kindle mounted on the Mac → copy the `.bin` into `mrpackages/`.
2. Clean up and **eject properly** (`scripts/prep-kindle-drive.sh`).
3. Unplug. On the Kindle: KUAL → Helper → *Install MR Packages* (or search `;log mrpi`).
4. Log: `extensions/MRInstaller/log/mrinstaller.log` on the Kindle drive. Look for `Hu oh... Got return code` after `Running 'install.sh' for 'usbnet ...'`.

A successful install creates `/usbnet/` (binaries, `etc/config`) **and** `extensions/usbnet/` (the KUAL menu). If the second is missing, the toggle won't work — see troubleshooting.

## Connect

1. KUAL → USBNetwork → toggle on (or `;un`). The Kindle disappears as a drive and shows up as **RNDIS/Ethernet Gadget** (here `en7`).
2. `scripts/mac-usbnet-setup.sh` sets the Mac to `192.168.15.201/24`.
3. `ssh root@192.168.15.244` (Kindle IP from `usbnet/etc/config`, `KINDLE_IP=`).

Toggle USBNetwork off to get the drive back.

## Config notes (`/mnt/us/usbnet/etc/config`)

- `USE_WIFI="false"` — leave off unless root has a real password / keys.
- `USE_OPENSSH="false"` — dropbear is the default server.
- Rename `usbnet/DISABLED_auto` → `auto` to start in network mode at boot (only once the config is known good).
- Keys go in `usbnet/etc/authorized_keys`.
