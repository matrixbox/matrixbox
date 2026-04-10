from __main__ import *
import sys, time, gc, math
import displayio, bitmaptools
import load_screen
from check_button import check_if_button_pressed
from load_screen import *
#microcontroller.cpu.frequency = 240000000
with open("clock.html") as f: html_body = f.read()

DISP_W = settings["width"]
DISP_H = settings["height"]

try:
    with open("clocksettings.txt") as f:
        clocksettings = json.loads(f.read())
except:
    clocksettings = {"f_color":"white",
    "b_color":"black",
    "inverted":0,
    "font":"large"
    }

for _k, _v in [("show_date", 1), ("show_day", 1), ("show_seconds", 0), ("show_temp", 0), ("city", ""), ("f_hex", "#ffffff"), ("b_hex", "#000000"), ("scale", 1), ("mode", "digital"), ("hour_hex", "#ffffff"), ("min_hex", "#4488ff"), ("sec_hex", "#ff4444"), ("show_border", 1), ("h12", 0), ("blink_colon", 1), ("rainbow", 0), ("accent", 0), ("accent_hex", "#4488ff"), ("show_dots", 1), ("dots_hex", "#ffffff")]:
    if _k not in clocksettings: clocksettings[_k] = _v

def hex_to_rgb(h):
    h = h.lstrip('#')
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

def apply_colors():
    fg = hex_to_rgb(clocksettings["f_hex"])
    bg = hex_to_rgb(clocksettings["b_hex"])
    palette[0] = (0, 0, 0)
    palette[5] = fg
    palette[12] = (fg[0] // 4, fg[1] // 4, fg[2] // 4)
    palette[13] = (fg[0] // 6, fg[1] // 6, fg[2] // 6)
    palette[14] = bg
    # analog hand colors
    hr_c = hex_to_rgb(clocksettings["hour_hex"])
    mn_c = hex_to_rgb(clocksettings["min_hex"])
    sc_c = hex_to_rgb(clocksettings["sec_hex"])
    palette[15] = hr_c
    palette[16] = mn_c
    palette[17] = sc_c
    dt_c = hex_to_rgb(clocksettings["dots_hex"])
    palette[18] = dt_c
    ac = hex_to_rgb(clocksettings["accent_hex"])
    palette[19] = ac

def _hsv_to_rgb(h):
    """h in 0..360, full saturation/value, returns (r,g,b) 0-255"""
    h = h % 360
    s = 6
    i = h // 60
    f = h - i * 60
    q = (60 - f) * 255 // 60
    t = f * 255 // 60
    if i == 0: return (255 // s, t // s, 0)
    if i == 1: return (q // s, 255 // s, 0)
    if i == 2: return (0, 255 // s, t // s)
    if i == 3: return (0, q // s, 255 // s)
    if i == 4: return (t // s, 0, 255 // s)
    return (255 // s, 0, q // s)

def selectfont(selectedfont):
    global clocksettings
    if selectedfont == "mini": load_screen.currentfont = font_mini
    if selectedfont == "small": load_screen.currentfont = font_small
    if selectedfont == "large": load_screen.currentfont = font_large
    clocksettings["font"] = selectedfont
    return load_screen.currentfont

load_screen.currentfont = selectfont(clocksettings["font"])



@ampule.route("/exit", method="GET")
def exit_webinterface(request):
    load_settings.app_running = False
    return (200, {}, """<meta http-equiv="refresh" content="0; url=../" />""")

@ampule.route("/", method="GET")
def webinterface(request):
    return (200, {}, header("Clock", app=True) + html_body + footer())

@ampule.route("/settings", method="GET")
def get_settings(request):
    return (200, {}, json.dumps(clocksettings))

@ampule.route("/", method="POST")
def clock_webinterface_post(request):
    #global f_color, b_color, inverted
    global clocksettings, delay, temp_string
    print("POSTED")
    print(request.params)
    print(request.body)
    if "save" in request.params:
        #clearscreen(True)
        with open("clocksettings.txt", "w") as f:
            f.write(json.dumps(clocksettings))
        #clearscreen(False)
        delay = 0
    if "size" in request.params: 
        selectfont(request.params["size"])
        rebuild_display()
        delay = 0
    if "f_hex" in request.params:
        clocksettings["f_hex"] = "#" + request.params["f_hex"]
        apply_colors()
        delay = 0
    if "b_hex" in request.params:
        clocksettings["b_hex"] = "#" + request.params["b_hex"]
        apply_colors()
        delay = 0
    if "show_date" in request.params:
        clocksettings["show_date"] = int(request.params["show_date"])
        delay = 0
    if "show_day" in request.params:
        clocksettings["show_day"] = int(request.params["show_day"])
        delay = 0
    if "show_seconds" in request.params:
        clocksettings["show_seconds"] = int(request.params["show_seconds"])
        delay = 0
    if "scale" in request.params:
        clocksettings["scale"] = int(request.params["scale"])
        rebuild_display()
        delay = 0
    if "show_temp" in request.params:
        clocksettings["show_temp"] = int(request.params["show_temp"])
        if clocksettings["show_temp"] and clocksettings.get("city", ""):
            try: temp_string = fetch_temperature()
            except: pass
        delay = 0
    if "city" in request.params:
        clocksettings["city"] = request.params["city"]
        if clocksettings["show_temp"] and clocksettings["city"]:
            try: temp_string = fetch_temperature()
            except: pass
        delay = 0
    if "mode" in request.params:
        clocksettings["mode"] = request.params["mode"]
        rebuild_display()
        delay = 0
    if "hour_hex" in request.params:
        clocksettings["hour_hex"] = "#" + request.params["hour_hex"]
        apply_colors()
        delay = 0
    if "min_hex" in request.params:
        clocksettings["min_hex"] = "#" + request.params["min_hex"]
        apply_colors()
        delay = 0
    if "sec_hex" in request.params:
        clocksettings["sec_hex"] = "#" + request.params["sec_hex"]
        apply_colors()
        delay = 0
    if "show_border" in request.params:
        clocksettings["show_border"] = int(request.params["show_border"])
        _last_analog = ""
        delay = 0
    if "show_dots" in request.params:
        clocksettings["show_dots"] = int(request.params["show_dots"])
        _last_analog = ""
        delay = 0
    if "dots_hex" in request.params:
        clocksettings["dots_hex"] = "#" + request.params["dots_hex"]
        apply_colors()
        _last_analog = ""
        delay = 0
    if "h12" in request.params:
        clocksettings["h12"] = int(request.params["h12"])
        delay = 0
    if "blink_colon" in request.params:
        clocksettings["blink_colon"] = int(request.params["blink_colon"])
        delay = 0
    if "rainbow" in request.params:
        clocksettings["rainbow"] = int(request.params["rainbow"])
        if not clocksettings["rainbow"]:
            apply_colors()
        delay = 0
    if "accent" in request.params:
        clocksettings["accent"] = int(request.params["accent"])
        delay = 0
    if "accent_hex" in request.params:
        clocksettings["accent_hex"] = "#" + request.params["accent_hex"]
        apply_colors()
        delay = 0
    return (200, {}, "ok")

def update_datetime():
    with pool.socket() as s:
        s.settimeout(5)
        s.connect(("data.t-skylt.se", 89))
        s.sendall(b"GET / HTTP/1.0\r\nHost: data.t-skylt.se\r\n\r\n")
        buf = bytearray(512)
        n = s.recv_into(buf)
        raw = buf[:n].decode("utf-8")
    # Extract full Date header: "Date: Sat, 22 Mar 2026 15:30:45 GMT"
    datestr = raw.split("Date:", 1)[1].split("\r\n")[0].strip()
    # datestr: "Sat, 22 Mar 2026 15:30:45 GMT"
    day_name = datestr[0:3]
    day_num = datestr[5:7]
    month = datestr[8:11]
    time_str = datestr[17:25]
    hour = str(int(time_str[0:2]))
    minute = str(int(time_str[3:5]))
    second = str(int(time_str[6:8]))
    if len(hour) == 1: hour = "0" + hour
    if len(minute) == 1: minute = "0" + minute
    if len(second) == 1: second = "0" + second
    return (hour, minute, second, day_name, day_num + " " + month)

def fetch_temperature():
    try:
        city = clocksettings.get("city", "")
        if not city: return ""
        response = requests.get("http://wttr.in/" + city.replace(" ", "+") + "?format=%t")
        data = response.text
        response.close()
        if data:
            temp = str(data).strip()
            clean = ""
            for c in temp:
                if c in "+-0123456789cf ":
                    clean += c
            return clean.strip()
    except:
        pass
    return ""

def _time_font_height():
    f = clocksettings["font"]
    if f == "large": return font_large["fontheight"]
    if f == "small": return font_small["fontheight"]
    return font_mini["fontheight"]

screen = None
BOX_PAD = 2
colon_on = True
_last_tstr = ""

def draw_rounded_box(bmp, x, y, w, h, border, fill):
    bitmaptools.fill_region(bmp, x + 1, y + 1, x + w - 1, y + h - 1, fill)
    for px in range(x + 1, x + w - 1):
        bmp[px, y] = border
        bmp[px, y + h - 1] = border
    for py in range(y + 1, y + h - 1):
        bmp[x, py] = border
        bmp[x + w - 1, py] = border

# --- Analog clock ---
_TWO_PI = 2.0 * math.pi

def _angle(value, total):
    return (value / total) * _TWO_PI - math.pi / 2.0

def _draw_hand(bmp, cx, cy, angle, length, cidx, thick=False):
    ex = int(cx + math.cos(angle) * length + 0.5)
    ey = int(cy + math.sin(angle) * length + 0.5)
    bitmaptools.draw_line(bmp, cx, cy, ex, ey, cidx)
    if thick:
        dx = int(math.cos(angle + math.pi / 2.0) + 0.5)
        dy = int(math.sin(angle + math.pi / 2.0) + 0.5)
        bitmaptools.draw_line(bmp, cx + dx, cy + dy, ex, ey, cidx)
        bitmaptools.draw_line(bmp, cx - dx, cy - dy, ex, ey, cidx)

def _draw_circle_outline(bmp, cx, cy, r, cidx):
    x = 0
    y = r
    d = 3 - 2 * r
    while x <= y:
        for px, py in [(cx+x,cy+y),(cx-x,cy+y),(cx+x,cy-y),(cx-x,cy-y),
                        (cx+y,cy+x),(cx-y,cy+x),(cx+y,cy-x),(cx-y,cy-x)]:
            if 0 <= px < bmp.width and 0 <= py < bmp.height:
                bmp[px, py] = cidx
        if d < 0:
            d += 4 * x + 6
        else:
            d += 4 * (x - y) + 10
            y -= 1
        x += 1

_last_analog = ""

def draw_analog(h, m, s):
    global _last_analog
    tag = str(h) + ":" + str(m) + ":" + str(s) if clocksettings["show_seconds"] else str(h) + ":" + str(m)
    if tag == _last_analog:
        return
    _last_analog = tag
    R = min(DISP_W, DISP_H) // 2 - 2
    cx = DISP_W // 2
    cy = DISP_H // 2
    bitmaptools.fill_region(screen, 0, 0, DISP_W, DISP_H, 14)
    if clocksettings["show_border"]:
        _draw_circle_outline(screen, cx, cy, R, 13)
    # 5-minute tick marks (12 dots, 1px, on the circle edge)
    if clocksettings["show_dots"]:
        for i in range(12):
            a = _angle(i, 12)
            tx = int(cx + math.cos(a) * R + 0.5)
            ty = int(cy + math.sin(a) * R + 0.5)
            if 0 <= tx < DISP_W and 0 <= ty < DISP_H:
                screen[tx, ty] = 18
    # hands
    h12 = (h % 12) + m / 60.0
    ha = _angle(h12, 12)
    ma = _angle(m, 60)
    _draw_hand(screen, cx, cy, ha, int(R * 0.5), 15, thick=True)
    _draw_hand(screen, cx, cy, ma, int(R * 0.8), 16, thick=True)
    if clocksettings["show_seconds"]:
        sa = _angle(s, 60)
        _draw_hand(screen, cx, cy, sa, int(R * 0.85), 17, thick=False)
    # center dot
    screen[cx, cy] = 5

def rebuild_display():
    global screen, _last_tstr, _last_analog
    screen = displayio.Bitmap(DISP_W, DISP_H, 20)
    tg = displayio.TileGrid(screen, pixel_shader=palette)
    root = displayio.Group()
    root.append(tg)
    display.root_group = root
    apply_colors()
    _last_tstr = ""
    _last_analog = ""
    gc.collect()

def draw_time(timestring, colon_vis=True):
    global _last_tstr
    f = load_screen.currentfont
    fh = _time_font_height()
    scale = clocksettings.get("scale", 1)

    # build display string with optional colon blink
    dstr = timestring
    if clocksettings["blink_colon"] and not colon_vis:
        dstr = dstr.replace(":", " ")

    # 12h conversion for display
    if clocksettings["h12"]:
        parts = timestring.split(":")
        h24 = int(parts[0])
        ampm = "am" if h24 < 12 else "pm"
        h12 = h24 % 12
        if h12 == 0: h12 = 12
        hstr = str(h12)
        if clocksettings["blink_colon"] and not colon_vis:
            dstr = hstr + " " + parts[1] if len(parts) == 2 else hstr + " " + parts[1] + " " + parts[2]
        else:
            dstr = hstr + ":" + parts[1] if len(parts) == 2 else hstr + ":" + parts[1] + ":" + parts[2]
        # reference string for stable box: widest 12h is "12:88" or "12:88:88"
        ref = "12:" + parts[1] if len(parts) == 2 else "12:" + parts[1] + ":" + parts[2]
    else:
        ampm = ""
        # reference string: always use colons for stable width
        ref = timestring

    tw = strlen(dstr, f)
    ref_w = strlen(ref, f)
    tmp = displayio.Bitmap(tw + 2, fh + 2, 20)
    pprint(dstr, 0, font=f, clear=False, color="white",
           top_offset=-1, _refresh=False, window=tmp, _clearscreen=False,
           block=True, shadow_color=12)
    sw = (ref_w + 2) * scale
    sh = (fh + 2) * scale

    # calculate info bar content
    info_parts = []
    if clocksettings["show_day"]:
        info_parts.append(day_name)
    if clocksettings["show_date"]:
        info_parts.append(date_str)
    if ampm:
        info_parts.append(ampm)
    if clocksettings["show_temp"] and temp_string:
        info_parts.append(temp_string)
    info_str = " . ".join(info_parts) if info_parts else ""
    info_h = 7 if info_str else 0  # mini font height + 1px gap

    # accent line
    accent_h = 2 if clocksettings["accent"] else 0

    # layout vertically centered
    total_h = sh + 2 * BOX_PAD + 2 + info_h + accent_h
    box_w = min(sw + 2 * BOX_PAD + 2, DISP_W)
    box_h = min(sh + 2 * BOX_PAD + 2, DISP_H)
    start_y = max((DISP_H - total_h) // 2, 0)
    box_x = max((DISP_W - box_w) // 2, 0)
    box_y = start_y

    bitmaptools.fill_region(screen, 0, 0, DISP_W, DISP_H, 0)
    draw_rounded_box(screen, box_x, box_y, box_w, box_h, 13, 14)

    if scale == 1:
        tx = box_x + (box_w - tw) // 2
        ty = box_y + BOX_PAD + 1
        bitmaptools.blit(screen, tmp, tx, ty,
                         x1=0, y1=0, x2=tmp.width, y2=tmp.height,
                         skip_source_index=0)
    else:
        bitmaptools.rotozoom(screen, tmp,
                             ox=DISP_W // 2, oy=box_y + box_h // 2,
                             px=tmp.width // 2, py=tmp.height // 2,
                             angle=0.0, scale=float(scale),
                             skip_index=0)

    # accent line below box
    if accent_h:
        ay = box_y + box_h + 1
        if ay < DISP_H:
            bitmaptools.fill_region(screen, box_x + 2, ay, box_x + box_w - 2, min(ay + 1, DISP_H), 19)

    # info bar below accent
    if info_str:
        iy = box_y + box_h + accent_h + 1
        iw = strlen(info_str, font_mini)
        ix = max((DISP_W - iw) // 2, 0)
        if iy + 5 <= DISP_H:
            info_tmp = displayio.Bitmap(iw + 1, 6, 20)
            pprint(info_str, 0, font=font_mini, clear=False, color="white",
                   top_offset=-1, _refresh=False, window=info_tmp, _clearscreen=False)
            # dim the info: swap palette 5 pixels to 18
            for py in range(info_tmp.height):
                for px in range(info_tmp.width):
                    if info_tmp[px, py] == 5:
                        info_tmp[px, py] = 18
            bitmaptools.blit(screen, info_tmp, ix, iy,
                             x1=0, y1=0, x2=info_tmp.width, y2=info_tmp.height,
                             skip_source_index=0)

    _last_tstr = timestring

dt = update_datetime()
hour, minute, second = dt[0], dt[1], dt[2]
day_name, date_str = dt[3], dt[4]
temp_string = ""
weather_counter = 0

if clocksettings["show_temp"] and clocksettings.get("city", ""):
    try: temp_string = fetch_temperature()
    except: pass

rebuild_display()

delay = 1
tick = 0
_colon_on = True
_rainbow_hue = 0

while load_settings.app_running:
    ampule.listen(socket)

    b = check_if_button_pressed()
    if b == 2: sys.exit()

    if clocksettings["show_seconds"]:
        timestring = hour + ":" + minute + ":" + second
    else:
        timestring = hour + ":" + minute
    
    _s = int(second)
    _s += 1
    if len(str(_s)) == 1: second = "0" + str(_s)
    else: second = str(_s)
    if second == "60": 
        delay = 0
        second = "00"
        try: 
            dt = update_datetime()
            hour, minute, second = dt[0], dt[1], dt[2]
            day_name, date_str = dt[3], dt[4]
        except: 
            _m  = int(minute)
            _m += 1
            if len(str(_m)) == 1: minute = "0" + str(_m)
            else: minute = str(_m)
            if minute == "60": 
                minute = "00"
                _h  = int(hour)
                _h += 1
                if len(str(_h)) == 1: hour = "0" + str(_h)
                else: hour = str(_h)
                if hour == "24": 
                    hour = "00"
        weather_counter += 1
        if clocksettings["show_temp"] and weather_counter >= 10:
            weather_counter = 0
            try: temp_string = fetch_temperature()
            except: pass

    # rainbow color cycling
    if clocksettings["rainbow"] and clocksettings["mode"] == "digital":
        _rainbow_hue = (_rainbow_hue + 3) % 360
        rgb = _hsv_to_rgb(_rainbow_hue)
        palette[5] = rgb
        palette[12] = (rgb[0] // 4, rgb[1] // 4, rgb[2] // 4)
        palette[18] = (rgb[0] // 3, rgb[1] // 3, rgb[2] // 3)
        _last_tstr = ""  # force redraw

    # colon blink toggle
    _colon_on = not _colon_on

    if clocksettings["mode"] == "analog":
        if timestring != _last_tstr or clocksettings["show_seconds"]:
            draw_analog(int(hour), int(minute), int(second))
    else:
        need_redraw = timestring != _last_tstr or clocksettings["blink_colon"]
        if need_redraw:
            draw_time(timestring, _colon_on)
    refresh()
    time.sleep(delay)
    if not delay: delay = 1
    refresh()
    time.sleep(delay)
    if not delay: delay = 1