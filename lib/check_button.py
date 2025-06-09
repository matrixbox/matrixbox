from __main__ import *
import digitalio, board
def time_button():
    return 1 - button.value

def check_if_button_pressed():
    z=0
    #time.sleep(debounce_delay)
    if time_button():
        time.sleep(debounce_delay)
        if time_button():
            time.sleep(debounce_delay*2)
            return 2
        return 1
    return z
    
    

button = digitalio.DigitalInOut(board.RX) # RX-pinnen för ena
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

gbutton = digitalio.DigitalInOut(board.TX) # TX-pinnena för andra
gbutton.direction = digitalio.Direction.INPUT
gbutton.pull = digitalio.Pull.DOWN

last_button_state = False

button_delay = 15000
debounce_delay = 0.3
short_button = 1000
long_button = 20000
if settings["width"] == 192 or settings["height"] == 64:
    short_button = 1000
    long_button = 2000