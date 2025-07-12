import sys, wifi, socketpool, ampule, time, os, json, microcontroller, storage
import load_settings
import digitalio, board
settings =  load_settings.settings()


from load_screen import *
import check_button
from check_button import *
# from check_button import check_if_button_pressed

def boot_splash():
    pprint("Booting...", line=0, color="red")

def check_if_button_pressed_on_boot():
    try:
        if check_if_button_pressed():
            return 1
        else: return 0
    except Exception as e: 
        print(e)
        return 1

def lock():
    storage.disable_usb_drive()
    storage.remount("/", False)
        
boot_splash()


if "unlock" in os.listdir():
    lock()
    try: os.remove("unlock")
    except: pass
    storage.enable_usb_drive()
    pprint("Unlocking filesystem")

elif check_if_button_pressed_on_boot():
    pprint("Unlocking filesystem")
else:
    lock()
    pprint("Locked filesystem")
    time.sleep(1)

try: clearscreen(True)
except Exception as e: pprint(str(e))

    
