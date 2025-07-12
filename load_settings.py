import json
from __main__ import *

def settings(): 
     settings = {"ssid":"T-Skylt WIFI",                                                      # Default settings:
                "password":"dunderskurre",
                "autostart":False,
                "rotation":0,
                "width":64,
                "height":32,
                "tiles":1,
                "repository_url":"https://raw.githubusercontent.com/matrixbox/matrixbox/refs/heads/main/", 
                "repository_file":"repository.txt",
                "wifi_power":16}

     try:
            with open("settings.txt") as f: settings.update(json.loads(f.read()))
            for setting in settings:
                _type = str
                try: 
                     int(settings[setting])
                     _type = int
                except: pass
                settings[setting] = _type(settings[setting])
                
     
     except Exception as e: 
         print("No previous settings!")
         print(e)
     return settings


    

app_running = False
latest_available_apps = []
