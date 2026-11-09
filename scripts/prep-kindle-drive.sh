#!/bin/sh
# Run while the Kindle is mounted as a drive (USBNetwork OFF), before ejecting.
# Stops Spotlight writing to it, removes macOS ._ files, checks/repairs FAT32, ejects.
V=/Volumes/Kindle
[ -d "$V" ] || { echo "Kindle not mounted at $V" >&2; exit 1; }

sudo mdutil -i off "$V"
touch "$V/.metadata_never_index"
rm -rf "$V/.Trashes/501" 2>/dev/null
find "$V" -name '._*' -type f -delete 2>/dev/null

if ! diskutil verifyVolume "$V"; then
  echo "Errors found, repairing..."
  diskutil repairVolume "$V" || diskutil repairVolume "$V"
fi
diskutil eject "$V"
