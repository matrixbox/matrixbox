from __main__ import *
import sys, time, gc
import displayio, bitmaptools
import load_screen
from check_button import check_if_button_pressed
from load_screen import *
microcontroller.cpu.frequency = 240000000
with open("clock.html") as f: html = f.read()

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

for _k, _v in [("show_date", 1), ("show_day", 1), ("show_seconds", 0), ("show_temp", 0), ("city", ""), ("f_hex", "#ffffff"), ("b_hex", "#000000"), ("scale", 1)]:
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
    return (200, {}, html)

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

def rebuild_display():
    global screen, _last_tstr
    screen = displayio.Bitmap(DISP_W, DISP_H, 20)
    tg = displayio.TileGrid(screen, pixel_shader=palette)
    root = displayio.Group()
    root.append(tg)
    display.root_group = root
    apply_colors()
    _last_tstr = ""
    gc.collect()

def draw_time(timestring):
    global _last_tstr
    f = load_screen.currentfont
    fh = _time_font_height()
    tw = strlen(timestring, f)
    scale = clocksettings.get("scale", 1)
    tmp = displayio.Bitmap(tw + 2, fh + 2, 20)
    pprint(timestring, 0, font=f, clear=False, color="white",
           top_offset=-1, _refresh=False, window=tmp, _clearscreen=False,
           block=True, shadow_color=12)
    sw = (tw + 2) * scale
    sh = (fh + 2) * scale
    box_w = min(sw + 2 * BOX_PAD + 2, DISP_W)
    box_h = min(sh + 2 * BOX_PAD + 2, DISP_H)
    box_x = max((DISP_W - box_w) // 2, 0)
    box_y = max((DISP_H - box_h) // 2, 0)
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
                             ox=DISP_W // 2, oy=DISP_H // 2,
                             px=tmp.width // 2, py=tmp.height // 2,
                             angle=0.0, scale=float(scale),
                             skip_index=0)
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

    if timestring != _last_tstr:
        draw_time(timestring)
    refresh()
    time.sleep(delay)
    if not delay: delay = 1