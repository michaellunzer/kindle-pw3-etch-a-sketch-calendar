#!/bin/sh
# Install hall-sensor/disable-hall.conf as an Upstart job on the Kindle and run it once.
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
CONF="$DIR/../hall-sensor/disable-hall.conf"
B64="$(base64 < "$CONF" | tr -d '\n')"

"$DIR/kssh.sh" "
set -e
mntroot rw
echo '$B64' | base64 -d > /etc/upstart/disable-hall.conf
sync
mntroot ro
initctl reload-configuration
initctl start disable-hall || true
echo hall_enable=\$(cat /sys/devices/system/wario_hall/wario_hall0/hall_enable)
"
