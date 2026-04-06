from __main__ import *
import sys, time, random, math
import load_screen
from check_button import check_if_button_pressed
from load_screen import *
microcontroller.cpu.frequency = 240000000

@ampule.route("/", method="GET")
def space_interface(request):
    return (200, {}, """<html><a href="/exit">&#x274C;</a></html>""")

@ampule.route("/exit", method="GET")
def exit_webinterface(request):
    load_settings.app_running = False
    return (200, {}, """<meta http-equiv="refresh" content="0; url=../" />""")

W = display_width()
H = display_height()
cx = W // 2
cy = H // 2
focal = 64

# Palette: space colors
palette[0] = (0, 0, 0)          # void
palette[1] = (12, 12, 20)       # dimmest star
palette[2] = (40, 40, 60)       # dim star
palette[3] = (100, 100, 130)    # medium star
palette[4] = (180, 180, 220)    # bright star
palette[5] = (255, 255, 255)    # brightest star core
palette[6] = (180, 80, 40)      # Mars / warm planet
palette[7] = (60, 100, 180)     # Neptune / cool planet
palette[8] = (200, 170, 100)    # Saturn / sandy planet
palette[9] = (100, 180, 100)    # green planet
palette[10] = (80, 60, 50)      # planet shadow
palette[11] = (200, 160, 60)    # ring / comet gold
palette[12] = (100, 140, 200)   # comet ice blue
palette[13] = (50, 70, 120)     # comet tail dim
palette[14] = (25, 35, 60)      # comet tail faint
palette[15] = (140, 50, 50)     # red dwarf star

# --- Stars (3D starfield) ---
NUM_STARS = 20
STAR_DEPTH = 200

def new_star():
    return [random.randint(-W, W),
            random.randint(-H, H),
            random.randint(20, STAR_DEPTH)]

stars = [new_star() for _ in range(NUM_STARS)]

# --- Planets ---
# [x3d, y3d, z, radius, color, ring]
planets = []
planet_timer = time.monotonic() + random.uniform(4, 8)

def spawn_planet():
    r = random.randint(3, 6)
    col = random.choice([6, 7, 8, 9])
    ring = random.random() < 0.35
    side = random.choice([-1, 1])
    return {"x": side * random.randint(W // 4, W),
            "y": random.randint(-H // 3, H // 3),
            "z": STAR_DEPTH + 40,
            "r": r, "col": col, "ring": ring}

def draw_circle(px, py, r, col, shadow_col):
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r:
                sx = px + dx
                sy = py + dy
                if 0 <= sx < W and 0 <= sy < H:
                    c = shadow_col if dx > r // 2 else col
                    pset(sx, sy, c)

def draw_ring(px, py, r, col):
    ring_r = r + 2
    for ang in range(0, 36):
        a = ang * 0.1745
        rx = int(px + math.cos(a) * ring_r)
        ry = int(py + math.sin(a) * (ring_r // 3))
        if 0 <= rx < W and 0 <= ry < H:
            pset(rx, ry, col)

# --- Comets ---
# [x, y, vx, vy, life, color]
comets = []
comet_timer = time.monotonic() + random.uniform(6, 12)

def spawn_comet():
    if random.random() < 0.5:
        x = -5
        vx = random.uniform(1.5, 3.0)
    else:
        x = W + 5
        vx = random.uniform(-3.0, -1.5)
    y = random.randint(2, H // 2)
    vy = random.uniform(0.2, 0.6)
    col = random.choice([11, 12])
    return {"x": float(x), "y": float(y), "vx": vx, "vy": vy,
            "life": 0, "col": col, "trail": []}

# --- Nebula dust (background shimmer) ---
nebula = []
for _ in range(15):
    nebula.append((random.randint(0, W - 1), random.randint(0, H - 1),
                   random.choice([1, 1, 14])))

frame = 0
speed = 3

while load_settings.app_running:
    window.fill(0)
    now = time.monotonic()

    # Nebula background shimmer
    for nx, ny, nc in nebula:
        if (frame + nx) % 8 < 5:
            pset(nx, ny, nc)

    # --- Stars ---
    for s in stars:
        s[2] -= speed
        if s[2] <= 1:
            s[0], s[1], s[2] = new_star()[0], new_star()[1], STAR_DEPTH

        # Project 3D -> 2D
        px = int(cx + (s[0] * focal) // s[2])
        py = int(cy + (s[1] * focal) // s[2])

        if 0 <= px < W and 0 <= py < H:
            # Brightness by depth
            depth_ratio = (STAR_DEPTH - s[2]) * 10 // STAR_DEPTH
            if depth_ratio < 2:
                col = 1
            elif depth_ratio < 4:
                col = 2
            elif depth_ratio < 6:
                col = 3
            elif depth_ratio < 8:
                col = 4
            else:
                col = 5
            pset(px, py, col)
            # Close stars get extra width
            if depth_ratio > 8 and px + 1 < W:
                pset(px + 1, py, 3)
        else:
            s[0], s[1], s[2] = new_star()[0], new_star()[1], STAR_DEPTH

    # --- Planets ---
    if now > planet_timer and len(planets) < 2:
        planets.append(spawn_planet())
        planet_timer = now + random.uniform(8, 15)

    alive_planets = []
    for p in planets:
        p["z"] -= 1
        if p["z"] < 5:
            continue
        px = int(cx + (p["x"] * focal) // p["z"])
        py = int(cy + (p["y"] * focal) // p["z"])
        # Radius scales with proximity
        vis_r = int(max(1, (p["r"] * focal) // p["z"]))
        if -vis_r < px < W + vis_r and -vis_r < py < H + vis_r:
            draw_circle(int(px), int(py), int(min(vis_r, 8)), p["col"], 10)
            if p["ring"] and vis_r > 2:
                draw_ring(int(px), int(py), int(min(vis_r, 8)), 11)
            alive_planets.append(p)
    planets = alive_planets

    # --- Comets ---
    if now > comet_timer and len(comets) < 1:
        comets.append(spawn_comet())
        comet_timer = now + random.uniform(8, 16)

    alive_comets = []
    for c in comets:
        c["x"] += c["vx"]
        c["y"] += c["vy"]
        c["life"] += 1
        # Store trail positions
        c["trail"].append((int(c["x"]), int(c["y"])))
        if len(c["trail"]) > 12:
            c["trail"].pop(0)

        # Draw trail (fading)
        tlen = len(c["trail"])
        for i, (tx, ty) in enumerate(c["trail"]):
            if 0 <= tx < W and 0 <= ty < H:
                if i < tlen // 3:
                    pset(tx, ty, 14)
                elif i < 2 * tlen // 3:
                    pset(tx, ty, 13)
                else:
                    pset(tx, ty, c["col"])

        # Bright head
        hx, hy = int(c["x"]), int(c["y"])
        if 0 <= hx < W and 0 <= hy < H:
            pset(hx, hy, 5)

        if -20 < c["x"] < W + 20 and -10 < c["y"] < H + 10:
            alive_comets.append(c)
    comets = alive_comets

    frame += 1
    refresh()
    ampule.listen(socket)

    b = check_if_button_pressed()
    if b: sys.exit()
