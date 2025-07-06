import load_screen, sys
from __main__ import *

exit = False
start_x = 300
padding_length = 30
default_offset = 0
default_scale = 1
scroll = 1
load_screen.currentfont = font_large
btc = 0
timer = time.monotonic()

with open("scroller.html") as f: html = f.read()


try:
    with open("scroller.txt") as f: scroller_text = f.read()
except: scroller_text = "http://" + str(wifi.radio.ipv4_address)# pangram. A pangram is a sentence that uses every letter of the alphabet. This phrase is often used for testing typewriters, keyboards, and fonts, as it covers all the necessary letters. It's also a useful tool for touch-typing practice"

@ampule.route("/exit", method="GET")
def webinterface(request):
    global exit
    exit = True
    return (200, {}, """<meta http-equiv="refresh" content="0; url=../" />""")

@ampule.route("/", method="POST")
def scroller_webinterface_port(request):
    global scroller_text, exit, default_offset, default_scale, btc, scroll, scroller_window, padding_length
    print("POSTED")
    print(request.params)
    print(request.body)
    if "btc" in request.params: btc = 1 - btc
    if "scroll" in request.params: 
        scroll = 1 - scroll
        scroller_window.x = 0-(padding_length)
        return (200, {}, "OK")
    if "text" in request.params: scroller_text = "        " + url_decoder(request.params["text"].replace("%20", " ") + "        ")
    if "size" in request.params: 
        if request.params["size"] == "mini": load_screen.currentfont = font_mini
        if request.params["size"] == "small": load_screen.currentfont = font_small
        if request.params["size"] == "large": load_screen.currentfont = font_large
    #if "exit" in request.params: exit = True
    if "color" in request.params: load_screen.currentcolor = request.params["color"]
    if "offset" in request.params: default_offset = int(request.params["offset"])
    if "scale" in request.params: default_scale = int(request.params["scale"])
    if "url" in request.body: 
        print("URL found")
        print(request.body)
    
    if btc: set_btc()
    else: set_text()

    return (200, {}, "OK")

@ampule.route("/", method="GET")
def scroller_webinterface(request):
    
    print(request.params)
    #set_text()
    return (200, {}, html)


clearscreen()

def padding(scroller_text): return "("*padding_length + scroller_text + "("*padding_length
def set_length(scroller_width):
    global window, default_scale
    window = displayio.Bitmap(scroller_width, 32, 10)
    scroller_window = displayio.TileGrid(window, pixel_shader=palette)
    scroller_screen = displayio.Group(scale=default_scale)
    scroller_screen.append(scroller_window)
    display.root_group = scroller_screen
    scroller_window.x = start_x
    microcontroller.cpu.frequency = 160000000
    if settings["width"] == 192: microcontroller.cpu.frequency = 240000000
    if settings["height"] == 64: microcontroller.cpu.frequency = 240000000
    return scroller_window

def set_text():
    global window
    global scroller_width, scroller_window, scroller_text
    scroller_width = strlen(padding(scroller_text), load_screen.currentfont)
    scroller_window = set_length(scroller_width)
    pprint(padding(scroller_text), line=0, font=load_screen.currentfont, color=load_screen.currentcolor,_refresh=False, window=window)

def set_btc():
    global scroller_text
    try:
        data = requests.get("https://min-api.cryptocompare.com/data/generateAvg?fsym=BTC&tsym=USD&e=coinbase").text
        data = json.loads(data)
        print(data)
        scroller_text = "₿ USD " + data["DISPLAY"]["PRICE"].replace("$ ", "").split(".")[0]
    except Exception as e:
        scroller_text = str(e)
    set_text()



set_text()

while not exit:
    ampule.listen(socket)
    scroller_window.y = default_offset
    if scroll:
        if scroller_window.x == -scroller_width + padding_length: 
            if btc and time.monotonic() > timer + 30: 
                timer = time.monotonic()
                set_btc()
            scroller_window.x = start_x
        scroller_window.x -= 1
    else:
        if btc and time.monotonic() > timer + 30: 
            timer = time.monotonic()
            set_btc()
            scroller_window.x = 0-(padding_length)
        
    refresh()
    b = check_if_button_pressed()
    if b == 2: sys.exit()

        
 

clearscreen()
