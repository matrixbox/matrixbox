from __main__ import *
import sys, time, random
import load_screen
from check_button import check_if_button_pressed
from load_screen import *
microcontroller.cpu.frequency = 180000000
import math, random

@ampule.route("/", method="GET")
def fireflies_interface(request):
    return (200, {}, """<html><a href="/exit">&#x274C;</a></html>""")
    

@ampule.route("/exit", method="GET")
def exit_webinterface(request):
    load_settings.app_running = False
    return (200, {}, """<meta http-equiv="refresh" content="0; url=../" />""")

center_x = settings["width"] // 2
center_y = settings["height"] // 2
num_arms = 3
stars_per_arm = 100
arm_tightness = 0.5
rotation_speed = 0.01

# Initialize stars positioned along spiral arms
stars = []
for arm in range(num_arms):
    for i in range(stars_per_arm):
        radius = i * 0.5
        angle = arm * (2 * math.pi / num_arms) + arm_tightness * math.log(radius + 1)
        angle += random.uniform(-0.1, 0.1)  # scatter
        color = random.randint(8, 15) if radius > 10 else random.randint(1, 7)  # bright core vs faded edge
        stars.append([radius, angle, rotation_speed, color])

while load_settings.app_running:
    window.fill(0)

    new_stars = []
    for radius, angle, speed, color in stars:
        x = int(center_x + math.cos(angle) * radius)
        y = int(center_y + math.sin(angle) * radius)
        x = max(0, min(settings["width"] - 1, x))
        y = max(0, min(settings["height"] - 1, y))

        pset(x, y, color)
        angle += speed  # rotate the star
        new_stars.append([radius, angle, speed, color])

    stars = new_stars
    refresh()
    ampule.listen(socket)

    b = check_if_button_pressed()
    if b == 2: sys.exit()
