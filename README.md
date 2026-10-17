# Forehead Frenzy

English charades for a room full of people. One phone goes on your forehead, everyone
else acts the word out, and you tilt the phone to score:

- **tilt the screen down** &rarr; they got it
- **tilt the screen up** &rarr; pass

1,672 easy words (A1&ndash;B1) across 23 topics, plus 4 mixed decks. Round lengths of
30 / 60 / 90 / 120 seconds, per-deck best scores, and a tap-the-screen mode for devices
that will not share their motion sensor.

Single file, no dependencies, no build step &mdash; `index.html` is the whole game.

## Why it has to be served over HTTPS

iOS only exposes `DeviceMotionEvent.requestPermission()` in a secure context, so the
tilt gesture is dead over `file://` or a plain-HTTP LAN address. It also needs to be a
**top-level** page: inside an iframe the sensor events are filtered out unless the frame
carries `allow="accelerometer; gyroscope"`. GitHub Pages satisfies both.

The setup screen prints a live diagnostics line (embedded / permission / event count /
tilt value) so a failure says which of those it was.

## How the tilt is measured

The signal is the gravity component along the screen normal (the device z axis), not the
`beta`/`gamma` orientation angles. Two reasons, both load-bearing:

1. Rotating about z leaves that component mathematically unchanged, so portrait, landscape
   and anything between all behave identically &mdash; and `screen.orientation` is never read,
   which is why the system rotation lock makes no difference.
2. Holding the phone against a forehead is `beta ~ 90`, the gimbal-lock singularity of the
   Z-X'-Y'' Euler convention, where angle readings jump around.

iOS and Android report `accelerationIncludingGravity` with opposite signs, so the page
self-calibrates: while the phone is held at a readable angle (away from the singularity) it
cross-checks the accelerometer's z sign against `cos(beta)cos(gamma)` from the orientation
event. A **Flip up/down** button overrides it if that ever guesses wrong.
