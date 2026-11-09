# Troubleshooting log

Every problem hit during this setup, in order, with the cause and fix.

## Wrong model assumed
**Symptom:** advice for the "2012 Paperwhite" didn't fit.
**Cause:** the device is a **7th gen = Paperwhite 3 (2015)**. 2012 = PW1, 2013 = PW2.
**Fix:** check Settings → Device Info, or `system/version.txt` on the drive (`Kindle 5.16.2.1.1`). PW3 uses the `pw2_and_up` packages and the `wario_hall` sysfs driver.

## MRPI: "No MR packages found"
**Cause:** the Kindle was **still mounted on the Mac**. While the host has the storage mounted, the Kindle can't see `/mnt/us`, so `mrpackages/` looks empty.
**Fix:** eject in Finder / `diskutil eject /Volumes/Kindle`, unplug, then run MRPI.

## `dot_clean` errors
```
Failed trying to change dir to .fseventsd
Merging /Volumes/Kindle/.Trashes/501/USBNetwork/... failed!
```
**Cause:** `.fseventsd` is protected; the merge failures were all inside the Mac's trash folder on the Kindle (an old, deleted USBNetwork copy).
**Fix:** skip `dot_clean`; delete AppleDouble files directly:
```sh
rm -rf /Volumes/Kindle/.Trashes/501
find /Volumes/Kindle -name '._*' -type f -delete 2>/dev/null
```

## `rm: ... Invalid argument` in `.Trashes`
**Cause:** corrupted FAT directory entries (there was also an `FSCK0000.REN` in `mrpackages/` from an earlier unclean unplug).
**Fix:** `diskutil repairVolume /Volumes/Kindle` (run twice if needed).

## "Package script install failed" / `;un` does nothing
From `extensions/MRInstaller/log/mrinstaller.log`:
```
cp: can't create directory '/mnt/us/./extensions/usbnet': Input/output error
Hu oh... Got return code 1 . . . :(
```
**Cause:** same filesystem corruption. `/usbnet` installed but the KUAL extension didn't, leaving an empty `extensions/usbnet/`, so there was no toggle.
`diskutil verifyVolume` still reported:
```
Warning: /.fseventsd has no clusters
Warning: Invalid long filename entry for /.Spotlight-V100/.../FSCK0000.REN
Error: -69845: File system verify or repair failed
```
**Fix:** `diskutil repairVolume`, `rmdir /Volumes/Kindle/extensions/usbnet`, re-run MRPI.

## Eject blocked by Spotlight
```
Unmount was dissented by PID ... (mdsync)
```
**Cause:** Spotlight indexing the Kindle — also a likely source of the corruption (`.Spotlight-V100` was where the bad entries were).
**Fix:**
```sh
sudo mdutil -i off /Volumes/Kindle
touch /Volumes/Kindle/.metadata_never_index
diskutil eject /Volumes/Kindle
```
Avoid `diskutil unmount force` — that's how FAT gets damaged.

## Kindle not reachable after toggling USBNetwork
**Cause:** macOS gave the RNDIS adapter a link-local `169.254.x.x` address.
**Fix:** `scripts/mac-usbnet-setup.sh` (`networksetup -setmanual "RNDIS/Ethernet Gadget" 192.168.15.201 255.255.255.0`).

## `Permission denied (publickey,password)`
**Cause:** SSH was run non-interactively (`BatchMode`), so no password was offered.
**Fix:** this dropbear accepted any password over USB — `scripts/kssh.sh` supplies one via `SSH_ASKPASS`. For a stricter setup, put a public key in `usbnet/etc/authorized_keys` (drive mode) instead.

## `mntroot: not found` / `initctl: not found`
**Cause:** non-interactive SSH sessions get a minimal `PATH`.
**Fix:** `export PATH=/usr/local/bin:/usr/sbin:/sbin:/usr/bin:/bin:$PATH` (built into `kssh.sh`). Because the install used `mntroot rw && ...`, nothing was written when it failed.

## Good habits
- Always eject before unplugging; run `scripts/prep-kindle-drive.sh`.
- Keep OTA updates blocked (`renameotabin`), and keep the jailbreak hotfix installed.
- Check `mrinstaller.log` first when an MR package fails.
