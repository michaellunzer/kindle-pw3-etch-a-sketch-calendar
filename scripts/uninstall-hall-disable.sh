#!/bin/sh
# Remove the Upstart job and turn the cover sensor back on.
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
"$DIR/kssh.sh" "
mntroot rw
rm -f /etc/upstart/disable-hall.conf
sync
mntroot ro
initctl reload-configuration
echo 1 > /sys/devices/system/wario_hall/wario_hall0/hall_enable
echo hall_enable=\$(cat /sys/devices/system/wario_hall/wario_hall0/hall_enable)
"
