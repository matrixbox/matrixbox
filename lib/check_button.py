from __main__ import *
import digitalio, board
def time_button():
    return 1 - button.value

_btn_state = 0  # 0=IDLE, 1=WAIT_DEBOUNCE, 2=WAIT_LONG, 3=WAIT_RELEASE
_btn_time = 0

def check_if_button_pressed():
    global _btn_state, _btn_time
    now = time.monotonic()
    pressed = time_button()

    if _btn_state == 0:
        if pressed:
            _btn_time = now
            _btn_state = 1
        return 0

    if _btn_state == 1:
        if now - _btn_time < debounce_delay:
            return 0
        if pressed:
            _btn_state = 2
        else:
            _btn_state = 0
            return 1
        return 0

    if _btn_state == 2:
        if now - _btn_time < debounce_delay * 3:
            if not pressed:
                _btn_state = 0
                return 1
            return 0
        _btn_state = 3
        return 2

    if _btn_state == 3:
        if not pressed:
            _btn_state = 0
        return 0

    return 0
    
    

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