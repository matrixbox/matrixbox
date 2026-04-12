import sys, json, time
import displayio

import load_screen
from __main__ import *
microcontroller.cpu.frequency = 240000000
exit_app = False

from font_large import font_large
from font_small import font_small
from font_mini import font_mini

FONTS = {"large": font_large, "small": font_small, "mini": font_mini}

# Custom font stored as string-based rows for full palette support
try:
    with open("/custom_font.json") as f:
        custom_font = json.load(f)
except:
    custom_font = {"fontheight": 8}

FONTS["custom"] = custom_font

CUSTOM_PATH = "/custom_font.json"

with open("charedit.html") as f:
    html_body = f.read()


def save_custom():
    with open(CUSTOM_PATH, "w") as f:
        json.dump(custom_font, f)


def font_list(font_name):
    """Return char list with widths and font height."""
    font = FONTS.get(font_name, font_large)
    fh = font.get("fontheight", 14)
    chars = {}
    for k, v in font.items():
        if k == "fontheight":
            continue
        if isinstance(v, list) and len(v) > 1:
            chars[k] = v[0]  # width
    return {"height": fh, "chars": chars}


def font_get_char(font_name, ch):
    """Return character grid as 2D array of palette indices."""
    font = FONTS.get(font_name, font_large)
    fh = font.get("fontheight", 14)
    if ch not in font:
        return {"width": 1, "height": fh, "grid": [[0] * 1 for _ in range(fh)]}
    glyph = font[ch]
    gw = glyph[0]
    grid = []
    for row_i in range(fh):
        row_data = glyph[row_i + 1] if row_i + 1 < len(glyph) else 0
        row = []
        if isinstance(row_data, int):
            # Bitmap: decode bits
            for x in range(gw):
                inv_x = gw - x
                bit = (row_data >> inv_x) & 1
                row.append(5 if bit else 0)  # 5=white, 0=black
            if len(row) < gw:
                row.extend([0] * (gw - len(row)))
        else:
            # String: each char is a palette index
            for x in range(gw):
                if x < len(str(row_data)):
                    row.append(int(str(row_data)[x]))
                else:
                    row.append(0)
        grid.append(row)
    return {"width": gw, "height": fh, "grid": grid}


def font_save_char(font_name, ch, width, grid):
    """Save character. For custom font: string-based. For built-in: bitmap."""
    font = FONTS.get(font_name)
    if font is None:
        return "Unknown font"
    fh = font.get("fontheight", len(grid))

    if font_name == "custom":
        # String-based: each row is a string of palette indices
        glyph = [width]
        for row in grid:
            glyph.append("".join(str(c) for c in row[:width]))
        # pad to fontheight
        while len(glyph) - 1 < fh:
            glyph.append("0" * width)
        font[ch] = glyph
        save_custom()
        return "Saved " + ch + " (custom)"
    else:
        # Bitmap: convert grid to int rows (any non-zero = 1)
        glyph = [width]
        for row in grid:
            val = 0
            for x in range(width):
                px = row[x] if x < len(row) else 0
                if px:
                    inv_x = width - x
                    val |= (1 << inv_x)
            glyph.append(val)
        while len(glyph) - 1 < fh:
            glyph.append(0)
        font[ch] = glyph
        # Save built-in font back to file
        _save_builtin(font_name, font)
        return "Saved " + ch + " (" + font_name + ")"


def font_delete_char(font_name, ch):
    font = FONTS.get(font_name)
    if font and ch in font and ch != "fontheight":
        del font[ch]
        if font_name == "custom":
            save_custom()
        else:
            _save_builtin(font_name, font)


def _save_builtin(font_name, font):
    """Write a built-in font dict back to its .py file."""
    path = "/lib/font_" + font_name + ".py"
    var = "font_" + font_name
    with open(path, "w") as f:
        f.write(var + " = {\n")
        f.write('  "fontheight":' + str(font["fontheight"]) + ",\n\n")
        for k, v in font.items():
            if k == "fontheight":
                continue
            f.write('  "' + k + '": [\n')
            f.write("    " + str(v[0]) + ",\n")
            for row_i in range(1, len(v)):
                row = v[row_i]
                if isinstance(row, int):
                    f.write("    " + bin(row) + ",\n")
                else:
                    f.write('    "' + str(row) + '",\n')
            f.write("  ],\n\n")
        f.write("}\n")


# ---------------------------------------------------------
#  WEB ROUTES
# ---------------------------------------------------------

@ampule.route("/exit", method="GET")
def web_exit(request):
    global exit_app
    exit_app = True
    return (200, {}, """<meta http-equiv="refresh" content="0; url=../" />""")


@ampule.route("/", method="GET")
def editor_get(request):
    if not request.params:
        return (200, {}, header("Char Editor", app=True) + html_body + footer())

    action = request.params.get("action", "")

    if action == "list":
        fname = request.params.get("font", "large")
        data = font_list(fname)
        return (200, {"Content-Type": "application/json"}, json.dumps(data))

    if action == "get":
        fname = request.params.get("font", "large")
        ch = url_decoder(request.params.get("char", "A"))
        data = font_get_char(fname, ch)
        return (200, {"Content-Type": "application/json"}, json.dumps(data))

    return (200, {}, header("Char Editor", app=True) + html_body + footer())


@ampule.route("/", method="POST")
def editor_post(request):
    action = request.params.get("action", "")

    if action == "save":
        try:
            body = request.body if hasattr(request, "body") else ""
            data = json.loads(body)
            fname = data.get("font", "custom")
            ch = data.get("char", "")
            width = data.get("width", 6)
            grid = data.get("grid", [])
            if not ch:
                return (200, {}, "No character specified")
            msg = font_save_char(fname, ch, width, grid)
            return (200, {}, msg)
        except Exception as e:
            return (200, {}, "Error: " + str(e))

    if action == "delete":
        fname = request.params.get("font", "custom")
        ch = url_decoder(request.params.get("char", ""))
        if ch:
            font_delete_char(fname, ch)
        return (200, {}, "OK")

    if action == "preview":
        txt = url_decoder(request.params.get("text", "Test"))
        fname = request.params.get("font", "large")
        font = FONTS.get(fname, font_large)
        clearscreen(lines=True)
        pprint(txt, line=0, font=font, color="white")
        return (200, {}, "OK")

    return (200, {}, "OK")


# ---------------------------------------------------------
#  INIT
# ---------------------------------------------------------
clearscreen()
pprint("Char Editor", line=0, color="white")

while not exit_app:
    ampule.listen(socket)
    b = check_if_button_pressed()
    if b == 2:
        sys.exit()

clearscreen()
