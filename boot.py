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

storage.remount("/", False)
        
boot_splash()


if check_if_button_pressed_on_boot() or "unlock" in os.listdir():
    pprint("Unlocking filesystem", line=1)
    try: os.remove("unlock")
    except: pass

else:
    storage.disable_usb_drive()
    pprint("Locked filesystem", line=1)
    time.sleep(1)
    