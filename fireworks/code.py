from __main__ import *
import sys, time, random
import load_screen
from check_button import check_if_button_pressed
from load_screen import *
microcontroller.cpu.frequency = 240000000
import math, random

@ampule.route("/", method="GET")
def fireflies_interface(request):
    return (200, {}, "<html><a href=\"/exit\">&#x274C;</a></html>")

@ampule.route("/exit", method="GET")
def exit_webinterface(request):
    load_settings.app_running = False
    return (200, {}, "<meta http-equiv=\"refresh\" content=\"0; url=../\" />")

width = settings["width"]
height = settings["height"]

def create_firework(x, y):
    particles = []
    num_particles = random.randint(50, 100)
    colors = [random.randint(1, 15) for _ in range(3)]
    for _ in range(num_particles):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1, 3)
        vx = speed * math.cos(angle)
        vy = speed * math.sin(angle)
        lifetime = random.randint(20, 40)
        color = random.choice(colors)
        particles.append({
            "x": x,
            "y": y,
            "vx": vx,
            "vy": vy,
            "lifetime": lifetime,
            "color": color
        })
    return particles

fireworks = []
last_firework_time = 0
firework_delay = 1  # seconds

while load_settings.app_running:
    current_time = time.monotonic()

    window.fill(0)

    # Create new fireworks randomly
    if current_time - last_firework_time > firework_delay and len(fireworks) < 3:
        x = random.randint(10, width - 10)
        y = random.randint(height // 4, height // 2)
        fireworks.append(create_firework(x, y))
        last_firework_time = current_time
        firework_delay = random.uniform(0.5, 2)

    # Update and draw particles
    new_fireworks = []
    for firework in fireworks:
        active_particles = []
        for particle in firework:
            particle["x"] += particle["vx"]
            particle["y"] += particle["vy"]
            particle["vy"] += 0.1  # Gravity

            particle["lifetime"] -= 1
            if particle["lifetime"] > 0 and 0 <= int(particle["x"]) < width and 0 <= int(particle["y"]) < height:
                pset(int(particle["x"]), int(particle["y"]), particle["color"])
                active_particles.append(particle)

        if active_particles:
            new_fireworks.append(active_particles)

    fireworks = new_fireworks

    refresh()
    ampule.listen(socket)

    b = check_if_button_pressed()
    if b: sys.exit()
