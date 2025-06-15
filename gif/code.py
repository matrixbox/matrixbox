from __main__ import *
from load_screen import *
import sys, board
import gifio
import time
from check_button import check_if_button_pressed

exit = False
clock_window = displayio.TileGrid(window, pixel_shader=palette)
splash = displayio.Group(scale=1)
splash.append(clock_window)
display.root_group = splash
clearscreen()
if "images" not in os.listdir(): 
    try: os.mkdir("images")
    except: pass
    

try:
    files = os.listdir("images")
    print(files)
except:
    print("Fail")
    print(os.listdir())
_index = 0

try:
    with open("gif.html") as f: html = f.read()
except: html = ""

@ampule.route("/exit", method="GET")
def webinterface(request):
    global exit
    exit = True
    return (200, {}, """<meta http-equiv="refresh" content="0; url=../" />""")

@ampule.route("/", method="GET")
def gif_webinterface(request):
    return (200, {}, """
<html>
<a href="/exit">&#x274C;</a><button style='background-color:#73a9ff' onclick="fetch('/?next=true', {method: 'POST'})">&#11179;</button>
            
<h1>GIF-webinterface</h1>

</html>
""")

@ampule.route('/', method="POST")
def webinterface_post(request):
    global _index
    print(_index)
    print(request.params)
    if "next" in request.params: 
        try:
            _index += 1
            load_img()
        except: 
            _index = 0
            load_img()
    
    return (200, {}, "OK")
    return (200, {}, """<meta http-equiv="refresh" content="0; url=../" />""")
    

def load_img():
    odg = gifio.OnDiskGif("images/"+files[_index])
    start = time.monotonic()
    next_delay = odg.next_frame() # Load the first frame
    end = time.monotonic()
    overhead = end - start
    face = displayio.TileGrid(
        odg.bitmap,
        pixel_shader=displayio.ColorConverter(
            input_colorspace=displayio.Colorspace.RGB565_SWAPPED,
            dither=True
        ),
    )
    splash.append(face)
    refresh()

if not os.listdir("images"): pprint("Upload image", _refresh=True)
else: load_img()
time.sleep(0.5)

while not exit:
    ampule.listen(socket)
    #time.sleep(0.01)
    """x = check_if_button_pressed() 
    if x: 
        _index += 1
        try: load_img()
        except: 
            _index = 0
            load_img()
        time.sleep(0.2)
        x = check_if_button_pressed()
        if x: sys.exit()"""
    b = check_if_button_pressed()
    #print(b)
    if b == 1:
        _index += 1
        try: load_img()
        except: 
            _index = 0
            load_img()
        time.sleep(0.2)
    elif b == 2: sys.exit()
