import json
import math
import sys

import ampule
import bitmaptools
import wifi
from check_button import check_if_button_pressed
from load_screen import (
    clearscreen,
    display,
    font_large,
    font_mini,
    font_small,
    palette,
    refresh,
    strlen,
    window,
)
from web_interface import footer, header

from __main__ import socket

exit_app = False
w = display.width
h = display.height

FONTS = {"mini": font_mini, "small": font_small, "large": font_large}

# Palette slots 0-11 are the only ones the kernel backs up/restores on app exit.
# Slot 0 is pinned to black (matches window.fill(0) used everywhere else); the
# other 11 slots are handed out to colors on a least-recently-used basis so an
# arbitrary number of distinct hex colors can still be requested over time.
COLOR_CACHE_SIZE = 11
_color_slots = {}  # hex -> slot
_color_lru = []  # hex values, oldest first


def hex_to_rgb(value: str) -> tuple:
    value = value.lstrip("#").lower()
    if len(value) != 6:
        return (255, 255, 255)

    try:
        return (int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16))
    except ValueError:
        return (255, 255, 255)


def color_slot(value: str) -> int:
    value = value.lstrip("#").lower()
    if value in ("", "000000"):
        return 0

    if value in _color_slots:
        _color_lru.remove(value)
        _color_lru.append(value)
        return _color_slots[value]

    if len(_color_lru) < COLOR_CACHE_SIZE:
        slot = len(_color_lru) + 1
    else:
        oldest = _color_lru.pop(0)
        slot = _color_slots.pop(oldest)

    palette[slot] = hex_to_rgb(value)
    _color_slots[value] = slot
    _color_lru.append(value)

    return slot


def circle_points(cx: int, cy: int, r: int):
    """Midpoint circle algorithm; yields the 8-way symmetric outline points."""
    x, y = r, 0
    err = 0

    while x >= y:
        yield (cx + x, cy + y)
        yield (cx + y, cy + x)
        yield (cx - y, cy + x)
        yield (cx - x, cy + y)
        yield (cx - x, cy - y)
        yield (cx - y, cy - x)
        yield (cx + y, cy - x)
        yield (cx + x, cy - y)

        y += 1
        if err <= 0:
            err += 2 * y + 1
        if err > 0:
            x -= 1
            err -= 2 * x + 1


def draw_text(text: str, font: dict, slot: int, x0: int, y0: int) -> None:
    is_mini = font is font_mini
    fh = font["fontheight"]
    px = 0

    for ch in text:
        lookup = ch.lower() if is_mini else ch
        glyph = font.get(lookup, font.get("_"))
        if glyph is None:
            continue

        gw = glyph[0]
        for col in range(gw):
            inv = gw - col
            for row in range(fh):
                if (glyph[row + 1] >> inv) & 1:
                    x, y = x0 + px + col, y0 + row
                    if 0 <= x < w and 0 <= y < h:
                        window[x, y] = slot

        px += gw


with open("remotecanvas.html") as f:
    html_body = f.read()


@ampule.route("/exit", method="GET")
def api_exit(request):
    global exit_app
    exit_app = True

    return (200, {}, """<meta http-equiv="refresh" content="0; url=../" />""")


@ampule.route("/", method="GET")
def api_home(request):
    ip = str(wifi.radio.ipv4_address) if wifi.radio.ipv4_address else "OFFLINE"
    body = (
        html_body.replace("__IP__", ip)
        .replace("__WIDTH__", str(w))
        .replace("__HEIGHT__", str(h))
    )

    return (200, {}, header("Remote Canvas", app=True) + body + footer())


@ampule.route("/info", method="GET")
def api_info(request):
    return (
        200,
        {"Content-Type": "application/json"},
        json.dumps({"width": w, "height": h}),
    )


@ampule.route("/background", method="POST")
def api_background(request):
    try:
        data = json.loads(request.body)
        slot = color_slot(str(data.get("color", "#000000")))
        window.fill(slot)
        refresh()
    except Exception as e:
        print("background err:", e)
        return (400, {}, str(e))

    return (200, {}, "ok")


@ampule.route("/rect", method="POST")
def api_rect(request):
    try:
        data = json.loads(request.body)
        x0, x1 = sorted((int(data["x0"]), int(data["x1"])))
        y0, y1 = sorted((int(data["y0"]), int(data["y1"])))
        x0, y0 = max(x0, 0), max(y0, 0)
        x1, y1 = min(x1, w - 1), min(y1, h - 1)

        fill_color = data.get("fill_color")
        if fill_color:
            slot = color_slot(str(fill_color))
            bitmaptools.fill_region(window, x0, y0, x1 + 1, y1 + 1, slot)

        border_color = data.get("border_color")
        if border_color:
            slot = color_slot(str(border_color))
            bitmaptools.draw_line(window, x0, y0, x1, y0, slot)
            bitmaptools.draw_line(window, x0, y1, x1, y1, slot)
            bitmaptools.draw_line(window, x0, y0, x0, y1, slot)
            bitmaptools.draw_line(window, x1, y0, x1, y1, slot)

        refresh()
    except Exception as e:
        print("rect err:", e)
        return (400, {}, str(e))

    return (200, {}, "ok")


@ampule.route("/pixel", method="POST")
def api_pixel(request):
    try:
        data = json.loads(request.body)
        x, y = int(data["x"]), int(data["y"])
        slot = color_slot(str(data.get("color", "#ffffff")))

        if 0 <= x < w and 0 <= y < h:
            window[x, y] = slot

        refresh()
    except Exception as e:
        print("pixel err:", e)
        return (400, {}, str(e))

    return (200, {}, "ok")


@ampule.route("/line", method="POST")
def api_line(request):
    try:
        data = json.loads(request.body)
        x0 = min(max(int(data["x0"]), 0), w - 1)
        y0 = min(max(int(data["y0"]), 0), h - 1)
        x1 = min(max(int(data["x1"]), 0), w - 1)
        y1 = min(max(int(data["y1"]), 0), h - 1)
        slot = color_slot(str(data.get("color", "#ffffff")))

        bitmaptools.draw_line(window, x0, y0, x1, y1, slot)
        refresh()
    except Exception as e:
        print("line err:", e)
        return (400, {}, str(e))

    return (200, {}, "ok")


@ampule.route("/circle", method="POST")
def api_circle(request):
    try:
        data = json.loads(request.body)
        cx, cy = int(data["x"]), int(data["y"])
        r = max(int(data["radius"]), 0)

        fill_color = data.get("fill_color")
        if fill_color:
            slot = color_slot(str(fill_color))
            for dy in range(-r, r + 1):
                y = cy + dy
                if not 0 <= y < h:
                    continue

                dx = int(math.sqrt(r * r - dy * dy))
                x0 = max(cx - dx, 0)
                x1 = min(cx + dx, w - 1)
                if x0 <= x1:
                    bitmaptools.draw_line(window, x0, y, x1, y, slot)

        border_color = data.get("border_color")
        if border_color:
            slot = color_slot(str(border_color))
            for x, y in circle_points(cx, cy, r):
                if 0 <= x < w and 0 <= y < h:
                    window[x, y] = slot

        refresh()
    except Exception as e:
        print("circle err:", e)
        return (400, {}, str(e))

    return (200, {}, "ok")


@ampule.route("/text", method="POST")
def api_text(request):
    try:
        data = json.loads(request.body)
        text = str(data.get("text", ""))
        font = FONTS.get(data.get("font_size", "small"), font_small)
        slot = color_slot(str(data.get("color", "#ffffff")))
        fh = font["fontheight"]
        tw = strlen(text, font)
        padding = int(data.get("padding", 0))

        if "x" in data:
            x0 = int(data["x"])
        else:
            align = data.get("align", "left")
            if align == "center":
                x0 = max((w - tw) // 2, 0)
            elif align == "right":
                x0 = max(w - tw - padding, 0)
            else:
                x0 = padding

        if "y" in data:
            y0 = int(data["y"])
        else:
            valign = data.get("valign", "top")
            if valign == "center":
                y0 = max((h - fh) // 2, 0)
            elif valign == "bottom":
                y0 = max(h - fh - padding, 0)
            else:
                y0 = padding

        draw_text(text, font, slot, x0, y0)
        refresh()
    except Exception as e:
        print("text err:", e)
        return (400, {}, str(e))

    return (200, {}, "ok")


clearscreen(lines=True)
window.fill(0)
refresh()

while not exit_app:
    ampule.listen(socket)
    if check_if_button_pressed() == 2:
        sys.exit()
