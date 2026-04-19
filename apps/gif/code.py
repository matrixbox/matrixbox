from __main__ import *
from load_screen import *
import sys, board, binascii
import gifio
import time
from check_button import check_if_button_pressed

exit = False
brightness_shift = 2  # 0=full, 1=1/2, 2=1/4, 3=1/8
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
    with open("gif.html") as f: html_body = f.read()
except: html_body = ""

@ampule.route("/exit", method="GET")
def webinterface(request):
    global exit
    exit = True
    return (200, {}, """<meta http-equiv="refresh" content="0; url=../" />""")

@ampule.route("/", method="GET")
def gif_webinterface(request):
    return (200, {}, header("GIF Player", app=True) + html_body + footer())

@ampule.route('/', method="POST")
def webinterface_post(request):
    global _index, brightness_shift
    print("POST:ed")
    print(_index)
    print(request.params)
    print(request.body)
    
    
    
    if "next" in request.params: 
        print(request.params["next"])
        try:
            _index += 1
            load_img()
        except: 
            _index = 0
            load_img()
        return

    if "brightness" in request.params:
        try:
            brightness_shift = int(request.params["brightness"])
            if brightness_shift < 0: brightness_shift = 0
            if brightness_shift > 4: brightness_shift = 4
        except: pass
        return (200, {}, "OK")
    
    if "sendbase64" in request.params:
        print("SEND")
        try:
            img = request.body
            print(type(img))
            #img = bytes(request.body, 'utf-8')
            print(len(img))
            #img = binascii.unhexlify(img)
            img = binascii.a2b_base64(img)
            print(img)
            #img = bytes(img)
            with open("images/uploaded.gif", "wb") as f:
                f.write(img)
            #load_img(img)
        except Exception as e: print(e)

        #try: 
        #    print("trying to save")
        #    file_bytes = bytes(request.body)
        #    with open("uploaded.gif", "wb") as f:
        #        f.write(file_bytes)
        #    print(f"Received {len(file_bytes)} bytes")
        #except Exception as e: print(e)
    #return (200, {}, "OK")
    return (200, {}, """<meta http-equiv="refresh" content="0; url=../" />""")
    

def dim_frame(bmp, w, h, shift):
    if shift == 0:
        return
    for y in range(h):
        for x in range(w):
            v = bmp[x, y]
            if v == 0:
                continue
            # swap bytes: RGB565_SWAPPED -> standard RGB565
            s = ((v & 0xFF) << 8) | ((v >> 8) & 0xFF)
            r = (s >> 11) & 0x1F
            g = (s >> 5) & 0x3F
            b = s & 0x1F
            r >>= shift
            g >>= shift
            b >>= shift
            s = (r << 11) | (g << 5) | b
            bmp[x, y] = ((s & 0xFF) << 8) | ((s >> 8) & 0xFF)

def load_img(file=False):
    if file: pass
    else: file = "images/"+files[_index]
    odg = gifio.OnDiskGif(file)
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
    return odg

if not os.listdir("images"): pprint("Upload image", _refresh=True)
else: odg = load_img()
time.sleep(0.5)

while not exit:
    ampule.listen(socket)
    time.sleep(0.01)
    odg.next_frame()
    dim_frame(odg.bitmap, odg.bitmap.width, odg.bitmap.height, brightness_shift)
    refresh()
    
    b = check_if_button_pressed()
    #print(b)
    if b == 1:
        _index += 1
        try: odg = load_img()
        except: 
            _index = 0
            odg = load_img()
        time.sleep(0.2)
    elif b == 2: sys.exit()
