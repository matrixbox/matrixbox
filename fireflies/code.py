from __main__ import *
import sys, time, random
import load_screen
from check_button import check_if_button_pressed
from load_screen import *
microcontroller.cpu.frequency = 180000000


import random

# initialize firefly positions
#fireflies = [(random.randint(0, 63), random.randint(0, 31)) for _ in range(10)]

@ampule.route("/", method="GET")
def fireflies_interface(request):
    return (200, {}, """<html><a href="/exit">&#x274C;</a></html>""")
    

@ampule.route("/exit", method="GET")
def exit_webinterface(request):
    load_settings.app_running = False
    return (200, {}, """<meta http-equiv="refresh" content="0; url=../" />""")

width = settings["width"] - 1
height = settings["height"] - 1

fireflies = [(random.randint(0, width), random.randint(0, height), random.randint(1, 15)) for _ in range(10)]

while load_settings.app_running:
    # erase current firefly positions
    for x, y, _ in fireflies:
        pset(x, y, 0)

    # move each firefly randomly and redraw with its own color
    new_fireflies = []
    for x, y, color in fireflies:
        dx = random.choice([-1, 0, 1])
        dy = random.choice([-1, 0, 1])
        nx = max(0, min(width, x + dx))
        ny = max(0, min(height, y + dy))
        new_fireflies.append((nx, ny, color))
        pset(nx, ny, color)

    fireflies = new_fireflies
    refresh()



    ampule.listen(socket)
    
    b = check_if_button_pressed()
    if b == 2: sys.exit()


    