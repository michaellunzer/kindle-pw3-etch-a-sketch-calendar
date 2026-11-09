#!/bin/sh
# Run a command on the Kindle over USBNetwork without an interactive prompt.
# USBNetwork's dropbear accepted any password over USB, so a dummy password is
# fed via SSH_ASKPASS (macOS has no sshpass). Usage: ./kssh.sh 'command'
#
# Set KINDLE_IP to override the default.
KINDLE_IP="${KINDLE_IP:-192.168.15.244}"
mkdir -p "$HOME/.kindle-ssh"
ASK="$(mktemp -t kpass)"
trap 'rm -f "$ASK"' EXIT
printf '#!/bin/sh\necho x\n' > "$ASK"
chmod 700 "$ASK"

SSH_ASKPASS="$ASK" SSH_ASKPASS_REQUIRE=force DISPLAY=:0 \
  ssh -T \
    -o StrictHostKeyChecking=accept-new \
    -o UserKnownHostsFile="$HOME/.kindle-ssh/known_hosts" \
    -o PubkeyAuthentication=no \
    -o ConnectTimeout=8 \
    -o LogLevel=ERROR \
    root@"$KINDLE_IP" "export PATH=/usr/local/bin:/usr/sbin:/sbin:/usr/bin:/bin:\$PATH; $*" </dev/null \
  | grep -v 'Welcome to Kindle'
