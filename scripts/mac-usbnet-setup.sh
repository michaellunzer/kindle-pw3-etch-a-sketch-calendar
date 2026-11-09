#!/bin/sh
# Give the Mac a static address on the Kindle's USB network adapter.
# With USBNetwork on, the Kindle appears as "RNDIS/Ethernet Gadget" and macOS
# only self-assigns a 169.254.x.x address, so the Kindle (192.168.15.244) is
# unreachable until this is set.
set -e
PORT="RNDIS/Ethernet Gadget"
networksetup -listallhardwareports | grep -q "$PORT" || {
  echo "No '$PORT' adapter. Is USBNetwork toggled on and the cable plugged in?" >&2
  exit 1
}
networksetup -setmanual "$PORT" 192.168.15.201 255.255.255.0
sleep 2
ping -c 2 -t 3 192.168.15.244 && echo "Kindle reachable at 192.168.15.244"
