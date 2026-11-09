# Disabling the magnetic cover sensor

The Paperwhite has a hall effect sensor that sleeps/wakes the device when a magnetic case cover closes/opens. Caseless use (or a faulty sensor, or a magnet nearby) causes spurious sleep/wake. On this device it can be turned off in software.

## The sysfs knobs (PW3 / "wario" kernel)

Found with `find /sys -iname '*hall*'`:

```
/sys/devices/system/wario_hall/wario_hall0/
  hall_detect       current magnet state (0 = no magnet)
  hall_enable       1 = sensor active, 0 = ignored   <-- the one that matters
  hall_debug
  hall_trig_wkup
  hall_gpio_pullup
/sys/class/misc/hall
```

Values observed before the change: `hall_detect=0 hall_enable=1 hall_debug=0 hall_trig_wkup=0 hall_gpio_pullup=0`.

## One-off (until reboot)

```sh
echo 0 > /sys/devices/system/wario_hall/wario_hall0/hall_enable
```

Tested by closing the case / holding a magnet over the sensor: the device stayed awake, and the value was still `0` a few minutes later (powerd didn't reset it).

## Permanent: Upstart job

[`disable-hall.conf`](disable-hall.conf) is installed as `/etc/upstart/disable-hall.conf`. It follows the same pattern NiLuJe's hacks use (e.g. `linkss.conf`, `usbnet.conf` in the same directory):

- `start on started powerd` — run after the power daemon is up, so powerd can't reset it at startup
- `task` — runs once and exits
- skips itself if `/mnt/us/ENABLE_HALL` exists (an easy, no-SSH way to undo it)
- `sleep 5` — small margin after powerd starts

The root filesystem is read-only ext3; it is remounted briefly to install:

```sh
export PATH=/usr/sbin:/sbin:/usr/bin:/bin:$PATH   # non-interactive SSH has a tiny PATH
mntroot rw
cp disable-hall.conf /etc/upstart/disable-hall.conf
sync
mntroot ro
initctl reload-configuration
```

`scripts/install-hall-disable.sh` does all of this from the Mac.

### Verifying without rebooting

```sh
H=/sys/devices/system/wario_hall/wario_hall0/hall_enable
echo 1 > $H; cat $H          # 1
initctl start disable-hall   # "disable-hall stop/waiting" (task finished)
cat $H                       # 0
```

## Undo

- Easiest: create an empty `ENABLE_HALL` file at the root of the Kindle drive, reboot.
- Remove completely: `scripts/uninstall-hall-disable.sh` (deletes the job and writes `1` back).

## Hardware alternative (not used)

iFixit has a guide for this exact model (PW3) that disconnects the sensor's flex cable. Reports say it can also kill the frontlight. It does **not** work on the original 2012 Paperwhite (EY21), whose firmware treats a missing sensor as "cover closed". KOReader also has an option that uses the same sysfs knob, but it only applies while KOReader is running — the Upstart job covers the stock UI too.
