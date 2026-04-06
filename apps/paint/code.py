import load_screen, sys, json
from __main__ import *

exit_app = False
w = display.width
h = display.height

with open("interface.html") as f:
    html_body = f.read().replace("__WIDTH__", str(w)).replace("__HEIGHT__", str(h))

# Build palette color table for JS: index -> [r, g, b]
palette_colors = {}
for i in range(12):
    try:
        c = palette[i]
        if isinstance(c, int):
            palette_colors[i] = [(c >> 16) & 0xFF, (c >> 8) & 0xFF, c & 0xFF]
        else:
            palette_colors[i] = [c[0], c[1], c[2]]
    except:
        pass

html_body = html_body.replace("__PALETTE__", json.dumps(palette_colors))

@ampule.route("/exit", method="GET")
def paint_exit(request):
    global exit_app
    exit_app = True
    return (200, {}, """<meta http-equiv="refresh" content="0; url=../" />""")

@ampule.route("/", method="GET")
def paint_home(request):
    return (200, {}, header("Paint", app=True) + html_body + footer())

@ampule.route("/px", method="POST")
def paint_pixel(request):
    try:
        data = json.loads(request.body)
        c = int(data["c"])
        for pt in data["pts"]:
            x, y = int(pt[0]), int(pt[1])
            if 0 <= x < w and 0 <= y < h:
                window[x, y] = c
        display.refresh()
    except Exception as e:
        print("px err:", e)
    return (200, {}, "ok")

@ampule.route("/fill", method="POST")
def paint_fill(request):
    try:
        data = json.loads(request.body)
        sx = int(data["x"])
        sy = int(data["y"])
        c = int(data["c"])
        if sx < 0 or sx >= w or sy < 0 or sy >= h:
            return (200, {}, "ok")
        target = window[sx, sy]
        if target == c:
            return (200, {}, "ok")
        stack = [(sx, sy)]
        visited = set()
        while stack:
            x, y = stack.pop()
            if (x, y) in visited:
                continue
            if x < 0 or x >= w or y < 0 or y >= h:
                continue
            if window[x, y] != target:
                continue
            visited.add((x, y))
            window[x, y] = c
            stack.append((x + 1, y))
            stack.append((x - 1, y))
            stack.append((x, y + 1))
            stack.append((x, y - 1))
        display.refresh()
    except Exception as e:
        print("fill err:", e)
    return (200, {}, "ok")

@ampule.route("/clear", method="POST")
def paint_clear(request):
    window.fill(0)
    display.refresh()
    return (200, {}, "ok")

SAVE_DIR = "saves"
try: os.mkdir(SAVE_DIR)
except: pass

def _safe_name(name):
    return "".join(c for c in name if c.isalnum() or c in "_-")[:20]

@ampule.route("/saves", method="GET")
def paint_list_saves(request):
    try:
        files = [f.replace(".json", "") for f in os.listdir(SAVE_DIR) if f.endswith(".json")]
    except:
        files = []
    return (200, {"Content-Type": "application/json"}, json.dumps(files))

@ampule.route("/save", method="POST")
def paint_save(request):
    try:
        data = json.loads(request.body)
        name = _safe_name(data["name"])
        if not name:
            return (400, {}, "bad name")
        rows = []
        for y in range(h):
            row = []
            for x in range(w):
                row.append(window[x, y])
            rows.append(row)
        with open(SAVE_DIR + "/" + name + ".json", "w") as f:
            json.dump({"w": w, "h": h, "d": rows}, f)
    except Exception as e:
        print("save err:", e)
        return (500, {}, str(e))
    return (200, {}, "ok")

@ampule.route("/load", method="POST")
def paint_load(request):
    try:
        data = json.loads(request.body)
        name = _safe_name(data["name"])
        with open(SAVE_DIR + "/" + name + ".json") as f:
            img = json.load(f)
        rows = img["d"]
        window.fill(0)
        for y in range(min(h, len(rows))):
            for x in range(min(w, len(rows[y]))):
                window[x, y] = rows[y][x]
        display.refresh()
        return (200, {"Content-Type": "application/json"}, json.dumps({"d": rows}))
    except Exception as e:
        print("load err:", e)
        return (500, {}, str(e))

@ampule.route("/delete", method="POST")
def paint_delete(request):
    try:
        data = json.loads(request.body)
        name = _safe_name(data["name"])
        os.remove(SAVE_DIR + "/" + name + ".json")
    except Exception as e:
        print("del err:", e)
    return (200, {}, "ok")

clearscreen(lines=True)
window.fill(0)
display.refresh()

while not exit_app:
    ampule.listen(socket)
    b = check_if_button_pressed()
    if b == 2:
        sys.exit()