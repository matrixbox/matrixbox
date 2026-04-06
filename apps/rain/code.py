from __main__ import *
import sys, time, random
import load_screen
from check_button import check_if_button_pressed
from load_screen import *
microcontroller.cpu.frequency = 240000000

@ampule.route("/", method="GET")
def rain_interface(request):
    return (200, {}, """<html><a href="/exit">&#x274C;</a></html>""")

@ampule.route("/exit", method="GET")
def exit_webinterface(request):
    load_settings.app_running = False
    return (200, {}, """<meta http-equiv="refresh" content="0; url=../" />""")

width = display_width()
height = display_height()

# Rain palette setup: dark blue bg tones + bright rain colors
palette[0] = (0, 0, 0)         # black background
palette[1] = (20, 40, 80)      # dim blue - slow distant rain
palette[2] = (40, 70, 130)     # medium blue - mid rain
palette[3] = (90, 130, 200)    # bright blue - fast close rain
palette[4] = (160, 200, 255)   # white-blue - splash highlight
palette[5] = (6, 10, 25)       # very faint - cloud/atmosphere
palette[6] = (10, 20, 50)      # slightly brighter atmosphere
palette[7] = (200, 220, 255)   # bright splash

# --- Raindrops ---
# Each drop: [x, y (float), speed, length, color]
num_drops = 55
drops = []
for _ in range(num_drops):
    spd = random.uniform(0.5, 2.5)
    col = 1 if spd < 1.0 else (2 if spd < 1.7 else 3)
    ln = 1 if spd < 1.0 else (2 if spd < 1.7 else 3)
    drops.append([random.randint(0, width - 1),
                  random.uniform(-height, height - 1),
                  spd, ln, col])

# --- Splashes ---
# Each splash: [x, y, life, max_life]
splashes = []

# --- Cloud layer (top few rows, static shimmer) ---
cloud_pixels = []
for x in range(width):
    for y in range(0, 4):
        if random.random() < 0.35:
            cloud_pixels.append((x, y, random.choice([5, 5, 6])))

frame = 0

while load_settings.app_running:
    window.fill(0)

    # Draw clouds with subtle shimmer
    for cx, cy, cc in cloud_pixels:
        c = cc
        if frame % 12 == 0 and random.random() < 0.08:
            c = 6 if cc == 5 else 5
        pset(cx, cy, c)

    # Update and draw raindrops
    for d in drops:
        d[1] += d[2]  # move down by speed

        # Draw drop streak
        for t in range(d[3]):
            py = int(d[1]) - t
            if 0 <= d[0] < width and 0 <= py < height:
                pset(d[0], py, d[4])

        # Bright tip
        ty = int(d[1])
        if 0 <= d[0] < width and 0 <= ty < height:
            pset(d[0], ty, d[4] + 1)

        # When drop hits bottom, create splash and reset
        if d[1] >= height:
            if d[2] > 1.2:
                splashes.append([d[0], height - 1, 0, random.randint(3, 5)])
            d[0] = random.randint(0, width - 1)
            d[1] = random.uniform(-20, -1)
            d[2] = random.uniform(0.5, 2.5)
            d[4] = 1 if d[2] < 1.0 else (2 if d[2] < 1.7 else 3)
            d[3] = 1 if d[2] < 1.0 else (2 if d[2] < 1.7 else 3)

    # Draw and update splashes
    alive = []
    for s in splashes:
        life = s[2]
        mx = s[3]
        spread = life + 1
        bright = 4 if life < mx // 2 else 2
        # Small V-shape splash
        for dx in range(-spread, spread + 1):
            sy = s[1] - abs(dx)
            sx = s[0] + dx
            if 0 <= sx < width and 0 <= sy < height:
                pset(sx, sy, bright)
        s[2] += 1
        if s[2] < s[3]:
            alive.append(s)
    splashes = alive

    frame += 1
    refresh()
    ampule.listen(socket)

    b = check_if_button_pressed()
    if b: sys.exit()
