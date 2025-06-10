#from __main__ import *
import displayio, board, framebufferio, microcontroller, load_settings, os
from rgbmatrix import RGBMatrix
from microcontroller import watchdog
from font_mini import font_mini
from font_small import font_small
from font_large import font_large

settings =  load_settings.settings() # behövs för boot.py
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
window = displayio.Bitmap(128, 32, 10) # själva viewporten dit pixlar skrivs
line_window = [] # en lista för multi-line printout till skärmen
palette = displayio.Palette(10, dither=False)

tile_group = displayio.TileGrid(window, pixel_shader=palette)
rf_group = displayio.Group()
tile_groupgroup = displayio.Group()
tile_groupgroup.append(tile_group)
rf_group.append(tile_groupgroup)
display.root_group = rf_group

palette[0] = (0)    # vit
palette[1] = (50,50,00)    # vit
palette[2] = (50,50,50)    # vit
palette[3] = 0x000765      # morkbla
palette[4] = (100,0,0)     # rod
palette[5] = (20,20,20)    # grå
palette[6] = (20,20,40)    # grå
palette[7] = (0,20,0)    # grå
palette[8] = (20,20,20)    # grå
palette[9] = (0,0,0)    # grå

currentfont = font_mini 
currentcolor = "white"

def strlen(_string, font_size=font_mini): 
    if font_size==font_mini: _string = _string.lower()
    return sum((font_size[ascletters][0]) for ascletters in _string) # mäter längden på hel string

def pprint(string, line=False, color="white", font = font_mini, _refresh = True, clear=True, top_offset=0, window=window, _clearscreen=True):
    print(string)
    #string += (127 - strlen(string.lower())) * "("
    global line_window#, window
    if _clearscreen: string = string + "(" * (settings["width"] - strlen(string))


    if not "int" in str(type(line)):
        line_window.append(string)
        if len(line_window) > 5: line_window.pop(0)
        _lines = line_window
    else: 
        _lines = [string]
        line_window = [""* (int(line) + 1)]
        
    print(_lines)
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
    
    
    
    offs = 1 + top_offset
    for lin, stringline in enumerate(_lines):
        if line: lin = line
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
                    #else: window[width+pixwidth,(height)+offs] = int(font[character][height+1][width])
            if isinstance(font[character][1],int): pixwidth += font[character][0]
            else: pixwidth += len(font[character][1])
        pixwidth = 0
        if _refresh: refresh()

def clearscreen():
    global line_window
    window.fill(0)
    line_window = []
    refresh()

def refresh(): display.refresh()