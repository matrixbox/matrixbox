from __main__ import *

def settings(): 
    settings = {"ssid":"T-Skylt WIFI",                                                      # Default settings:
                "password":"dunderskurre",
                "autostart":False,
                "rotation":0,
                "width":128,
                "height":32,
                "tiles":1,
                "repository":{"url":"https://raw.githubusercontent.com/alex-t-84/pixelbox/refs/heads/main/", "file":"repository.txt"},
                "wifi_power":16}

    try:
            with open("settings.txt") as f: settings.update(json.loads(f.read()))
            print("Init.settings", settings)
            for setting in settings:
                _type = str
                try: 
                     int(settings[setting])
                     _type = int
                except: 
                     #float(settings[setting])
                     #_type = float
                     pass
                print(_type)
                settings[setting] = _type(settings[setting])
                print("Conv: ", settings)


    except Exception as e: 
         print("No previous settings!")
         print(e)
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