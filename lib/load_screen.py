from __main__ import * # antingen denna rad eller #settings = load_settings etc
import displayio, board, framebufferio, microcontroller, load_settings, os
from rgbmatrix import RGBMatrix
from microcontroller import watchdog
from font_mini import font_mini
from font_small import font_small
from font_large import font_large

#settings =  load_settings.settings() # behövs för boot.py
displayio.release_displays()

#from watchdog import WatchDogMode
#watchdog.timeout = 60
#watchdog.mode = WatchDogMode.RESET
#def wd(): return watchdog.feed()

if "DevKit" in os.uname().machine:
    _bit_depth = 4
    #_bit_depth = 5
    matrix = RGBMatrix(width=settings["width"], height=settings["height"], bit_depth=_bit_depth,
                    rgb_pins=[board.IO1,board.IO42,board.IO2, board.IO41,board.IO39,board.IO40],
                    addr_pins=[board.IO3, board.IO8, board.IO18, board.IO17],
                    clock_pin=board.IO12, latch_pin=board.IO13, output_enable_pin=board.IO14, tile=settings["tiles"],
                    serpentine=True, doublebuffer=True)
    

if os.uname().machine == "Waveshare ESP32-S3-Zero with ESP32S3": 
    _bit_depth = 5
    matrix = RGBMatrix(width=settings["width"], height=settings["height"], bit_depth=_bit_depth,
                    rgb_pins=[board.IO1,board.IO3,board.IO2, board.IO4,board.IO6,board.IO5],
                    addr_pins=[board.IO7, board.IO8, board.IO9, board.IO10],
                    clock_pin=board.IO11, latch_pin=board.IO12, output_enable_pin=board.IO13, tile=settings["tiles"],
                    serpentine=True, doublebuffer=True)

microcontroller.cpu.frequency = 180000000
print("--------------------------------------------------------- ")
print(" CHIP:           ", os.uname().machine)
print(" FREQUENCY:      ", microcontroller.cpu.frequency)
print("--------------------------------------------------------- ")

display = framebufferio.FramebufferDisplay(matrix, auto_refresh=False, rotation=settings["rotation"])
rf_group = displayio.Group()
display.root_group = rf_group
display.refresh()
display.root_group.hidden = True
rows = int((settings["height"]*1/32))
print(rows)
window = displayio.Bitmap(128, rows*32, 10) # själva viewporten dit pixlar skrivs
line_window = [] # en lista för multi-line printout till skärmen
palette = displayio.Palette(20, dither=False)

tile_group = displayio.TileGrid(window, pixel_shader=palette)
rf_group = displayio.Group()
tile_groupgroup = displayio.Group()
tile_groupgroup.append(tile_group)
rf_group.append(tile_groupgroup)
display.root_group = rf_group

palette[0] = (0)    # vit
palette[1] = (50,50,00)    # vit
palette[2] = (50,50,50)    # vit
palette[3] = (0, 59, 122)      # morkbla
palette[4] = (100,0,0)     # rod
palette[5] = (20,20,20)    # grey
palette[6] = (20,20,40)    #  ?
palette[7] = (0, 100, 10)      # green
palette[8] = (230, 28, 71)    # pink
palette[9] = (0,0,0)    # grå
palette[11] = (50,30,0)    # orange

currentfont = font_mini 
currentcolor = "white"

def strlen(_string, font_size=font_mini): 
    if font_size==font_mini: _string = _string.lower()
    return sum((font_size[ascletters][0]) for ascletters in _string) # mäter längden på hel string

def pprint(string, line=False, color="white", font = font_mini, _refresh = False, clear=True, top_offset=0, window=window, _clearscreen=True, hr="("):
    print(string)
    global line_window
    if _clearscreen: string = string + hr * (settings["width"] - strlen(string))
    
    max_lines = int(5*(settings["height"]*1/32)) #- 1

    if "int" in str(type(line)):
        _lines = [string]
        line_window = [""* (int(line) + 1)]
    else:
        line_window.append(string)
        if len(line_window) > max_lines: line_window.pop(0)
        _lines = line_window
    
    pixwidth = 0
    _color = False
    if color == "black": _color = (0)
    if color == "yellow": _color = (1)
    if color == "brightwhite": _color = (2)
    if color == "blue": _color = (3)
    if color == "red": _color = (4)
    if color == "white": _color = (5)
    if color == "light_blue": _color = (6)
    if color == "green": _color = (7)
    if color == "grey": _color = (8)
    if color == "black2": _color = (9)
    if color == "pink": _color = (10)
    if color == "orange": _color = (11)
    
    offs = 1 + top_offset
    try:
        for lin, stringline in enumerate(_lines):
            if line: lin = line
            if line == -1: lin = max_lines -1
            print(lin, len(_lines))
            for character in str(stringline):
                if font == font_mini: character = character.lower()
                if not character in font: 
                    print("Invalid character: ", character, " - ", string)
                    character = "_"
                for width in range(font[character][0]):
                    for height in range(font["fontheight"]):
                        invertedwidth = font[character][0] - width
                        if isinstance(font[character][1],int):
                            bit = ((font[character][height+1] >> invertedwidth) & 1)
                            if int(bit): window[width+pixwidth,((6*lin) + height)+offs] = _color
                            else: 
                                if clear: window[width+pixwidth,((6*lin) + height)+offs] = 0
                        else: window[width+pixwidth,(height)+offs] = int(font[character][height+1][width])
                if isinstance(font[character][1],int): pixwidth += font[character][0]
                else: pixwidth += len(font[character][1])
            pixwidth = 0
            if _refresh: refresh()
        if lin + 1 == len(_lines): refresh()
                #print("FULL STOP")

    except Exception as e:
        print(e)

def clearscreen():
    global line_window
    window.fill(0)
    line_window = []
    refresh()

def refresh(): display.refresh()
