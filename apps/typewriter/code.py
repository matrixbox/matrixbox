import sys, json
from __main__ import *
from load_screen import font_mini, font_small, font_large, window, pset

exit = False
with open("typewriter.html") as f: html_body = f.read()

_fonts = {"mini": font_mini, "small": font_small, "large": font_large}
_font_heights = {"mini": 6, "small": 8, "large": 16}
_cur_font = "mini"
_cmap = {"black":0,"yellow":1,"brightwhite":2,"blue":3,"red":4,"white":5,"light_blue":6,"green":7,"grey":8,"pink":10,"orange":11}

def _draw_char(x, y, ch, font, cidx):
    g = font.get(ch)
    if g is None: g = font.get("?")
    if g is None: return 4
    w = g[0]
    for row in range(len(g) - 1):
        bits = g[row + 1]
        if isinstance(bits, int):
            for col in range(w):
                if (bits >> (w - 1 - col)) & 1:
                    px = x + col
                    py = y + row
                    if 0 <= px < display.width and 0 <= py < display.height:
                        pset(px, py, cidx)
    return w

def _draw_seg(x, y, text, font, cidx):
    for ch in text:
        if ch == " ":
            x += 6
        else:
            x += _draw_char(x, y, ch, font, cidx)
    return x

def _render(lines_data):
    f = _fonts.get(_cur_font, font_mini)
    fh = _font_heights.get(_cur_font, 6)
    W = display.width
    H = display.height
    max_lines = H // fh
    clearscreen(False)
    window.fill(0)
    for i, segs in enumerate(lines_data[:max_lines]):
        x = 1
        y = i * fh + 1
        for seg in segs:
            t = seg.get("t", "")
            if _cur_font == "mini":
                t = t.lower()
            c = seg.get("c", "white")
            cidx = _cmap.get(c, 5)
            x = _draw_seg(x, y, t, f, cidx)
    refresh()

def _font_info():
    fh = _font_heights.get(_cur_font, 6)
    W = display.width
    H = display.height
    avg_cw = 4 if _cur_font == "mini" else 6 if _cur_font == "small" else 8
    cols = W // avg_cw
    rows = H // fh
    return json.dumps({"w": W, "h": H, "rows": rows, "cols": cols, "font": _cur_font})

@ampule.route("/exit", method="GET")
def _exit(request):
    global exit
    exit = True
    return (200, {}, """<meta http-equiv="refresh" content="0; url=../" />""")

@ampule.route("/tw/info", method="GET")
def _info(request):
    return (200, {}, _font_info())

@ampule.route("/", method="POST")
def _post(request):
    global _cur_font
    if "font" in request.params:
        _cur_font = request.params["font"]
    try:
        data = json.loads(request.body)
        _render(data)
    except Exception as e:
        print("tw post err:", e)
    return (200, {}, _font_info())

@ampule.route("/", method="GET")
def _get(request):
    return (200, {}, header("Typewriter", app=True) + html_body + footer())

clearscreen(lines=True)
pprint("Typewriter", line=0)
pprint("ready", line=1, color="yellow")
refresh()

while not exit:
    ampule.listen(socket)
    b = check_if_button_pressed()
    if b == 2: sys.exit()
        
 

