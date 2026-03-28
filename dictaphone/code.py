from __main__ import *
import sys, time
import load_screen
from check_button import check_if_button_pressed
from load_screen import *
microcontroller.cpu.frequency = 180000000

with open("interface.html") as f:
    html = f.read()

W = display_width()
H = display_height()

palette[0] = (0, 0, 0)
palette[1] = (50, 50, 0)
palette[2] = (50, 50, 50)
palette[3] = (0, 50, 100)
palette[5] = (40, 40, 40)
palette[8] = (20, 20, 20)

lines = []      # [(text, color), ...]
max_lines = H // 6
sentence_count = 0

def wrap_text(text, max_w):
    result = []
    words = text.split(" ")
    current = ""
    for w in words:
        test = (current + " " + w).strip()
        if strlen(test) <= max_w:
            current = test
        else:
            if current:
                result.append(current)
            current = w
            while strlen(current) > max_w and len(current) > 1:
                current = current[:-1]
    if current:
        result.append(current)
    return result

def show_lines():
    for i in range(max_lines):
        if i < len(lines):
            ln, col = lines[i]
            pprint(ln, line=i, color=col, clear=True, _clearscreen=True)
        else:
            pprint("", line=i, color="black", clear=True, _clearscreen=True)
    refresh()

def add_text(text):
    global lines, sentence_count
    text = text.strip()
    if text and text[-1] not in ".!?":
        text += "."
    col = "white" if sentence_count % 2 == 0 else "grey"
    sentence_count += 1
    wrapped = wrap_text(text, W - 2)
    for wl in wrapped:
        lines.append((wl, col))
    while len(lines) > max_lines:
        lines.pop(0)
    show_lines()

@ampule.route("/", method="GET")
def dictaphone_interface(request):
    return (200, {}, html)

@ampule.route("/exit", method="GET")
def exit_webinterface(request):
    load_settings.app_running = False
    return (200, {}, """<meta http-equiv="refresh" content="0; url=../" />""")

@ampule.route("/text", method="GET")
def receive_text(request):
    if "t" in request.params:
        txt = request.params["t"]
        for old, new in [("%20", " "), ("%C3%A5", "a"), ("%C3%A4", "a"), ("%C3%B6", "o"),
                         ("%C3%85", "a"), ("%C3%84", "a"), ("%C3%96", "o"),
                         ("%21", "!"), ("%3F", "?"), ("%2C", ","), ("%2E", ".")]:
            txt = txt.replace(old, new)
        print("DICTAPHONE:", txt)
        add_text(txt)
    return (200, {}, "ok")

@ampule.route("/clear", method="GET")
def clear_screen(request):
    global lines
    lines = []
    window.fill(0)
    refresh()
    return (200, {}, "ok")

pprint("dictaphone", line=0, color="white")
pprint("open web ui", line=1, color="white")
pprint("to start", line=2, color="white")

while load_settings.app_running:
    ampule.listen(socket)
    b = check_if_button_pressed()
    if b:
        sys.exit()
    time.sleep(0.05)