from __main__ import *
#import load_sacreen
import sys, time
import load_screen
from check_button import check_if_button_pressed
from load_screen import *
microcontroller.cpu.frequency = 180000000
with open("clock.html") as f: html = f.read()

try:
    with open("clocksettings.txt") as f:
        clocksettings = json.loads(f.read())
except:
    clocksettings = {"f_color":"white",
    "b_color":"black",
    "inverted":0,
    "font":"large"
    }

colorscheme = {"black2": (0),
        "black": (0),
         "grey": (30,30,30),
        "red": (30,0,0),
         "green": (0,30,0),
         "blue": (0,0,30),
         "yellow":(30,30,0),
         "white": (40,40,40)}

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

@ampule.route("/", method="POST")
def clock_webinterface_post(request):
    #global f_color, b_color, inverted
    global clocksettings, delay
    print("POSTED")
    print(request.params)
    print(request.body)
    if "save" in request.params:
        #clearscreen(True)
        with open("clocksettings.txt", "w") as f:
            f.write(json.dumps(clocksettings))
        #clearscreen(False)
        delay = 0
    if "invert" in request.params: 
        clocksettings["inverted"] = 1 - clocksettings["inverted"]
        palette[0] = (30,30, 30) if clocksettings["inverted"] else (0)
    if "size" in request.params: 
        selectfont(request.params["size"])
        
        window.fill(0)
    if "f_color" in request.params: clocksettings["f_color"] = request.params["f_color"]
    if "s_color" in request.params: clocksettings["b_color"] = request.params["s_color"]
    if "b_color" in request.params: 
        """if request.params["b_color"] == "black2": color = (0)
        if request.params["b_color"] == "grey": color = (30,30,30)
        if request.params["b_color"] == "red": color = (30,0,0)
        if request.params["b_color"] == "green": color = (0,30,0)
        if request.params["b_color"] == "blue": color = (0,0,30)
        if request.params["b_color"] == "yellow": color = (30,30,0)
        if request.params["b_color"] == "white": color = (40,40,40)"""
        clocksettings["b_color"] = request.params["b_color"]
        color = colorscheme[request.params["b_color"]]
        palette[0] = (color)
        

        #load_screen.currentcolor = request.params["color"]
    if "url" in request.body: 
        print("URL found")
        print(request.body)
    

def update_time():
    _time = fetch("data.t-skylt.se","", port=89, get_time=True)
    hour = str(int(_time[0:2]))
    minute = str(int(_time[3:5]))
    second = str(int(_time[6:8]))
    if len(hour) == 1: hour = "0" + hour
    if len(minute) == 1: minute = "0" + minute
    if len(second) == 1: second = "0" + second
    return (hour, minute, second)

show_seconds = False
_time = update_time()
hour, minute, second = _time[0], _time[1], _time[2]

clock_window = displayio.TileGrid(window, pixel_shader=palette)
clock_screen = displayio.Group(scale=2)
clock_screen.append(clock_window)
display.root_group = clock_screen
window.fill(0)
palette[0] = colorscheme[clocksettings["b_color"]]



def print_timestring(timestring, clear=False):
    #global f_color, b_color
    global clocksettings
    if clear == True:
        #pprint(timestring, 0, font=load_screen.currentfont, color=b_color, _refresh=False, top_offset=2)
        pprint("("+ timestring, 0, font=selectfont(clocksettings["font"]), clear=True, color=clocksettings["b_color"], top_offset=1, _refresh=False)
    else:
        #pprint(timestring, 0, font=load_screen.currentfont, color=b_color, _refresh=False, top_offset=2)
        pprint("("+ timestring, 0, font=selectfont(clocksettings["font"]), clear=False, color=clocksettings["f_color"], top_offset=1, _refresh=False)

delay = 1

while load_settings.app_running:
    ampule.listen(socket)
    
    b = check_if_button_pressed()
    if b == 2: sys.exit()
    
    timestring = hour + ":" + minute
    
    #refresh()
    
    _s = int(second)
    _s += 1
    if len(str(_s)) == 1: second = "0" + str(_s)
    else: second = str(_s)
    if second == "60": 
        #oldtimestring = timestring
        print_timestring(timestring, clear=True)
        delay = 0
        second = "00"
        try: 
            _time = update_time()
            hour, minute, second = _time[0], _time[1], _time[2]
        except: 
            _m  = int(minute)
            _m += 1
            if len(str(_m)) == 1: minute = "0" + str(_m)
            else: minute = str(_m)
            if minute == "60": 
                hour, minute, second = _time[0], _time[1], _time[2],
                minute = "00"
                _h  = int(hour)
                _h += 1
                if len(str(_h)) == 1: minute = "0" + str(_h)
                else: hour = str(_h)
                if hour == "24": 
                    hour = "00"
        
    if delay: print_timestring(timestring)
    refresh()
    time.sleep(delay)
    if not delay: delay = 1