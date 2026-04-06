from __main__ import *
import sys, time, gc
import load_screen
from check_button import check_if_button_pressed
from load_screen import *

microcontroller.cpu.frequency = 240000000

DISP_W = settings["width"]
DISP_H = settings["height"]

try:
    with open("stocksettings.txt") as f:
        cfg = json.loads(f.read())
except:
    cfg = {"symbols": "AAPL,MSFT,GOOG,AMZN,TSLA", "speed": 2, "interval": 60}

with open("stocks.html") as f: html_body = f.read()

# palette slots: 7=green, 4=red, 5=white/grey, 0=black
palette[0] = (0, 0, 0)
palette[4] = (200, 0, 0)
palette[5] = (50, 50, 50)
palette[7] = (0, 180, 0)
palette[1] = (80, 80, 0)

quotes = []  # list of (symbol, price, change_pct)

_font_map = {"small": font_small, "large": font_large}
current_font = _font_map.get(cfg.get("font", "small"), font_small)

def _fetch_one(sym):
    """Fetch a single symbol via Yahoo chart API. Returns (price, pct) or None."""
    try:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/" + sym + "?range=1d&interval=1d"
        resp = requests.get(url, headers={"User-Agent": "MatrixBox"})
        data = json.loads(resp.text)
        resp.close()
        meta = data["chart"]["result"][0]["meta"]
        price = meta["regularMarketPrice"]
        prev = meta["chartPreviousClose"]
        pct = ((price - prev) / prev) * 100 if prev else 0
        return (price, pct)
    except Exception as e:
        print("Fetch error for", sym, ":", e)
        try: resp.close()
        except: pass
        return None

def fetch_quotes():
    global quotes
    syms = cfg["symbols"].replace(" ", "")
    if not syms:
        return
    result = []
    for sym in syms.split(","):
        sym = sym.strip()
        if not sym:
            continue
        q = _fetch_one(sym)
        if q:
            result.append((sym, q[0], q[1]))
        gc.collect()
    quotes = result
    print("Fetched:", quotes)

def build_ticker_string():
    """Build a string like: AAPL 182.50 +1.2%  MSFT 415.20 -0.3%  ..."""
    parts = []
    for sym, price, pct in quotes:
        sign = "+" if pct >= 0 else ""
        p_str = str(price)
        # Truncate to 2 decimals
        if "." in p_str:
            whole, dec = p_str.split(".", 1)
            p_str = whole + "." + dec[:2]
        parts.append((sym.upper(), p_str, sign + "{:.1f}".format(pct) + "%", pct >= 0))
    return parts

def _safe_pset_bmp(bmp, x, y, c, bmp_w, bmp_h):
    if 0 <= x < bmp_w and 0 <= y < bmp_h:
        bmp[x, y] = c

def _draw_arrow_up(bmp, x, y, color, bmp_w, bmp_h):
    _safe_pset_bmp(bmp, x + 2, y, color, bmp_w, bmp_h)
    _safe_pset_bmp(bmp, x + 1, y + 1, color, bmp_w, bmp_h)
    _safe_pset_bmp(bmp, x + 2, y + 1, color, bmp_w, bmp_h)
    _safe_pset_bmp(bmp, x + 3, y + 1, color, bmp_w, bmp_h)
    _safe_pset_bmp(bmp, x + 2, y + 2, color, bmp_w, bmp_h)
    _safe_pset_bmp(bmp, x + 2, y + 3, color, bmp_w, bmp_h)
    _safe_pset_bmp(bmp, x + 2, y + 4, color, bmp_w, bmp_h)

def _draw_arrow_down(bmp, x, y, color, bmp_w, bmp_h):
    _safe_pset_bmp(bmp, x + 2, y, color, bmp_w, bmp_h)
    _safe_pset_bmp(bmp, x + 2, y + 1, color, bmp_w, bmp_h)
    _safe_pset_bmp(bmp, x + 2, y + 2, color, bmp_w, bmp_h)
    _safe_pset_bmp(bmp, x + 1, y + 3, color, bmp_w, bmp_h)
    _safe_pset_bmp(bmp, x + 2, y + 3, color, bmp_w, bmp_h)
    _safe_pset_bmp(bmp, x + 3, y + 3, color, bmp_w, bmp_h)
    _safe_pset_bmp(bmp, x + 2, y + 4, color, bmp_w, bmp_h)

def _render_text_to_bmp(bmp, string, start_x, y_top, color_idx, f, bmp_w, bmp_h):
    fh = f["fontheight"]
    px = start_x
    for ch in str(string):
        if ch not in f:
            ch = "_"
        glyph = f[ch]
        gw = glyph[0]
        is_bitmap = isinstance(glyph[1], int)
        if is_bitmap:
            for w in range(gw):
                sx = px + w
                if sx < 0 or sx >= bmp_w:
                    continue
                inv_w = gw - w
                for h in range(fh):
                    sy = y_top + h
                    if sy < 0 or sy >= bmp_h:
                        continue
                    bit = (glyph[h + 1] >> inv_w) & 1
                    if bit:
                        bmp[sx, sy] = color_idx
        px += gw
    return px

ticker_bmp = None
ticker_tg = None
ticker_w = 0

def build_ticker_bitmap():
    """Render all quotes into a wide bitmap. Called once when data or font changes."""
    global ticker_bmp, ticker_tg, ticker_w
    parts = build_ticker_string()
    if not parts:
        ticker_w = 0
        return

    f = current_font
    fh = f["fontheight"]
    gap = 8
    arrow_w = 6
    y_center = max(0, (DISP_H - fh) // 2)

    # Measure total width
    total_w = DISP_W  # start with padding so text scrolls in from right
    for sym, price, pct_str, up in parts:
        total_w += strlen(sym + " " + price + " ", f) + arrow_w + strlen(pct_str, f) + gap
    total_w += DISP_W  # end padding so last item scrolls fully off left

    ticker_bmp = displayio.Bitmap(total_w, DISP_H, 10)
    ticker_bmp.fill(0)

    px = DISP_W  # start drawing after initial padding
    for sym, price, pct_str, up in parts:
        color = 7 if up else 4
        px = _render_text_to_bmp(ticker_bmp, sym + " ", px, y_center, 5, f, total_w, DISP_H)
        px = _render_text_to_bmp(ticker_bmp, price + " ", px, y_center, color, f, total_w, DISP_H)
        if up:
            _draw_arrow_up(ticker_bmp, px, y_center, color, total_w, DISP_H)
        else:
            _draw_arrow_down(ticker_bmp, px, y_center, color, total_w, DISP_H)
        px += arrow_w
        px = _render_text_to_bmp(ticker_bmp, pct_str, px, y_center, color, f, total_w, DISP_H)
        px += gap

    ticker_w = total_w

    ticker_tg = displayio.TileGrid(ticker_bmp, pixel_shader=palette)
    ticker_tg.x = 0
    root = displayio.Group()
    root.append(ticker_tg)
    display.root_group = root
    gc.collect()

# Web interface
@ampule.route("/", method="GET")
def stock_interface(request):
    return (200, {}, header("Stocks", app=True) + html_body + footer())

@ampule.route("/exit", method="GET")
def exit_interface(request):
    load_settings.app_running = False
    return (200, {}, """<meta http-equiv="refresh" content="0; url=../" />""")

@ampule.route("/settings", method="GET")
def get_settings(request):
    return (200, {}, json.dumps(cfg))

@ampule.route("/quotes", method="GET")
def get_quotes(request):
    return (200, {}, json.dumps(quotes))

@ampule.route("/", method="POST")
def stock_post(request):
    global cfg
    print("POST:", request.params)
    rebuild = False
    if "symbols" in request.params:
        cfg["symbols"] = request.params["symbols"].upper()
        fetch_quotes()
        rebuild = True
    if "speed" in request.params:
        try: cfg["speed"] = int(request.params["speed"])
        except: pass
    if "interval" in request.params:
        try: cfg["interval"] = int(request.params["interval"])
        except: pass
    if "font" in request.params:
        global current_font
        cfg["font"] = request.params["font"]
        current_font = _font_map.get(cfg["font"], font_small)
        rebuild = True
    if rebuild:
        build_ticker_bitmap()
    if "save" in request.params:
        try:
            with open("stocksettings.txt", "w") as f:
                f.write(json.dumps(cfg))
        except: pass
    return (200, {}, "ok")

# Main loop
fetch_quotes()
build_ticker_bitmap()
last_fetch = time.monotonic()
speed_map = {1: 0.06, 2: 0.03, 3: 0.015}

while load_settings.app_running:
    if ticker_tg and ticker_w > 0:
        ticker_tg.x -= 1
        if ticker_tg.x < -ticker_w + DISP_W:
            ticker_tg.x = 0
        display.refresh()
    else:
        pprint("no data", 0)

    spd = speed_map.get(cfg.get("speed", 2), 0.03)
    time.sleep(spd)
    ampule.listen(socket)

    b = check_if_button_pressed()
    if b:
        load_settings.app_running = False

    # Periodic refresh
    if time.monotonic() - last_fetch > cfg.get("interval", 60):
        fetch_quotes()
        build_ticker_bitmap()
        last_fetch = time.monotonic()
        gc.collect()
