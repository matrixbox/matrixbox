import sys, json, time
import displayio
import bitmaptools
import wifi

import load_screen
from __main__ import *
microcontroller.cpu.frequency = 240000000
exit = False
padding_length = 20
default_offset = 0
default_scale = 1
scroll = 1
btc = 0
currency = "usd"
delay = 30
reverse_direction = 1   # 0 = left-to-right (normal), 1 = right-to-left
shadow_color = 0

shadow_color_map = {
    "black": 0,
    "yellow": 1,
    "brightwhite": 2,
    "blue": 3,
    "red": 4,
    "white": 5,
    "light_blue": 6,
    "green": 7,
    "grey": 8,
    "black2": 9,
    "pink": 10,
    "orange": 11,
}


load_screen.currentfont = font_large

with open("scroller.html") as f: html_body = f.read()

try:
    with open("scroller.txt") as f:
        scroller_text = f.read()
except:
    scroller_text = "http://" + str(wifi.radio.ipv4_address)

# ---------------------------------------------------------
#  GLOBALS FOR SCROLLER
# ---------------------------------------------------------

big_bitmap = None          # full text bitmap
viewport_bitmap = None     # 128x32 window
viewport_tg = None         # TileGrid for viewport
scroller_width = 0         # width of big_bitmap
scroll_x = 0               # current scroll offset

DISPLAY_WIDTH = settings["width"]
DISPLAY_HEIGHT = settings["height"]
PALETTE_SIZE = 10          # matches your existing palette

# ---------------------------------------------------------
#  HELPERS
# ---------------------------------------------------------

def padded(text):
    return " " * padding_length + text + " " * padding_length

def rebuild_scene():
    """Rebuild big bitmap, viewport, and display group based on current text/font/scale."""
    global big_bitmap, viewport_bitmap, viewport_tg, scroller_width, scroll_x

    text = padded(scroller_text)
    font = load_screen.currentfont

    scroller_width = strlen(text, font)
    if scroller_width < 1:
        scroller_width = 1

    # Full text bitmap
    big_bitmap = displayio.Bitmap(scroller_width, DISPLAY_HEIGHT, PALETTE_SIZE)

    # Render text once into big bitmap
    pprint(
        text,
        line=0,
        font=font,
        color=load_screen.currentcolor,
        _refresh=False,
        window=big_bitmap,
        block=True,     # <-- enable shadow
        shadow_color=shadow_color  # <-- use red for shadow
    )


    # Viewport bitmap (fixed display size)
    viewport_bitmap = displayio.Bitmap(DISPLAY_WIDTH, DISPLAY_HEIGHT, PALETTE_SIZE)

    # TileGrid for viewport
    viewport_tg = displayio.TileGrid(
        viewport_bitmap,
        pixel_shader=palette,
        x=0,
        y=default_offset,
    )

    # Group and root
    group = displayio.Group(scale=default_scale)
    group.append(viewport_tg)
    display.root_group = group

    # Reset scroll position
    scroll_x = DISPLAY_WIDTH  # start off-screen to the right

def blit_viewport():
    """Copy the visible slice from big_bitmap into viewport_bitmap based on scroll_x."""
    if big_bitmap is None or viewport_bitmap is None:
        return

    global scroll_x
    src_start = max(scroll_x, 0)
    src_end = min(scroll_x + DISPLAY_WIDTH, scroller_width)

    #if src_end <= src_start: return  # no overlap, nothing to draw

    width = src_end - src_start
    if width <= 0: return

    dst_x = max(0, -scroll_x)

    bitmaptools.blit(
        viewport_bitmap,
        big_bitmap,
        dst_x,
        0,
        x1=src_start,
        y1=0,
        x2=src_start + width,
        y2=DISPLAY_HEIGHT,
    )

# ---------------------------------------------------------
#  WEB ROUTES
# ---------------------------------------------------------

@ampule.route("/exit", method="GET")
def web_exit(request):
    global exit
    exit = True
    return (200, {}, """<meta http-equiv="refresh" content="0; url=../" />""")

@ampule.route("/", method="POST")
def scroller_post(request):
    global scroller_text, exit, default_offset, default_scale, shadow_color
    global btc, scroll, padding_length, scroll_x, reverse_direction

    if "btc" in request.params:
        btc = 1 - btc

    if "scroll" in request.params:
        scroll = 1 - scroll
        if scroll:
            scroll_x = DISPLAY_WIDTH
        else:
            scroll_x = strlen(" " * padding_length, load_screen.currentfont)
        return (200, {}, "OK")

    if "text" in request.params:
        scroller_text = padded(url_decoder(request.params["text"]))
    if "reverse" in request.params:
        try:
            reverse_direction = int(request.params["reverse"])
        except:
            reverse_direction = 1 - reverse_direction
        return (200, {}, "OK")

    if "size" in request.params:
        size = request.params["size"]
        if size == "mini":
            load_screen.currentfont = font_mini
        if size == "small":
            load_screen.currentfont = font_small
        if size == "large":
            load_screen.currentfont = font_large

    if "color" in request.params:
        load_screen.currentcolor = request.params["color"]

    if "offset" in request.params:
        default_offset = int(request.params["offset"])

    if "scale" in request.params:
        default_scale = int(request.params["scale"])
    
    if "shadow_color" in request.params:
        name = request.params["shadow_color"]
        if name in shadow_color_map:
            shadow_color = shadow_color_map[name]
        rebuild_scene()
        return (200, {}, "OK")



    if btc:
        set_btc()
    else:
        rebuild_scene()

    return (200, {}, "OK")

@ampule.route("/", method="GET")
def scroller_get(request):
    return (200, {}, header("Scroller", app=True) + html_body + footer())

# ---------------------------------------------------------
#  BTC TEXT
# ---------------------------------------------------------

def set_btc():
    global scroller_text
    try:
        data = requests.get(
            "https://min-api.cryptocompare.com/data/generateAvg?fsym=BTC&tsym=USD&e=coinbase"
        ).text
        data = json.loads(data)
        scroller_text = "₿ $" + data["DISPLAY"]["PRICE"].replace("$ ", "").split(".")[0]
    except Exception as e:
        scroller_text = str(e)

    rebuild_scene()

# ---------------------------------------------------------
#  INITIALIZE
# ---------------------------------------------------------

clearscreen()
rebuild_scene()

# ---------------------------------------------------------
#  MAIN LOOP
# ---------------------------------------------------------

while not exit:
    ampule.listen(socket)

    if scroll:
        if reverse_direction == 0:
            scroll_x -= 1
            if scroll_x <= -scroller_width: scroll_x = DISPLAY_WIDTH + scroller_width
        else: # L
            scroll_x += 1
            if scroll_x >= DISPLAY_WIDTH + scroller_width: scroll_x = -scroller_width



    blit_viewport()
    refresh()

    b = check_if_button_pressed()
    if b == 1:
        scroll = 1 - scroll
        if scroll:
            scroll_x = DISPLAY_WIDTH
    if b == 2:
        sys.exit()

clearscreen()
