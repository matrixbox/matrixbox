from __main__ import *

def settings(): 
    settings = {"ssid":"T-Skylt WIFI",                                                      # Default settings:
                "password":"dunderskurre",
                "autostart":False,
                "rotation":0,
                "width":128,
                "height":32,
                "tiles":1}

    try:
            with open("settings.txt") as f: settings.update(json.loads(f.read()))
    except: print("No previous settings")
    return settings

def savesettings(settings):
    print("Saving...")
    try:
        with open("settings.txt","w") as f:
            f.write(json.dumps(settings))
    except:
         print("Read only!")
    

app_running = False
latest_available_apps = []