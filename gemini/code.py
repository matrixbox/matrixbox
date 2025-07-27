from __main__ import *
try: import requests, json
except: pass
#import json

code = """from __main__ import *
import sys, time, random
import load_screen
from check_button import check_if_button_pressed
from load_screen import *
microcontroller.cpu.frequency = 240000000
import math, random

@ampule.route("/", method="GET")
def fireflies_interface(request):
    return (200, {}, "<html><a href="/exit">&#x274C;</a></html>")
    

@ampule.route("/exit", method="GET")
def exit_webinterface(request):
    load_settings.app_running = False
    return (200, {}, "<meta http-equiv="refresh" content="0; url=../" />")

import math, random

center_x = settings["width"] // 2
center_y = settings["height"] // 2
num_stars = 10

# Initialize stars with random positions and orbital speeds
stars = []
for _ in range(num_stars):
    angle = random.uniform(0, 2 * math.pi)
    radius = random.uniform(5, min(center_x, center_y) - 2)
    speed = random.uniform(0.01, 0.05)
    color = random.randint(1, 3)
    stars.append([angle, radius, speed, color])

while load_settings.app_running:
    window.fill(0)

    new_stars = []
    for angle, radius, speed, color in stars:
        x = int(center_x + math.cos(angle) * radius)
        y = int(center_y + math.sin(angle) * radius)
        pset(x, y, color)
        angle += speed
        radius += 0.05  # slight outward drift
        if radius < min(center_x, center_y):
            new_stars.append([angle, radius, speed, color])
        else:
            # Reset star to the center
            angle = random.uniform(0, 2 * math.pi)
            radius = 5
            speed = random.uniform(0.01, 0.05)
            color = random.randint(1, 15)
            new_stars.append([angle, radius, speed, color])

    stars = new_stars
    refresh()
    ampule.listen(socket)

    b = check_if_button_pressed()
    if b: sys.exit()"""

prompt = """

Look at the code above and imagine that your response code must adhere to the same general strucutre. Can you come up with a brand new pattern?
Please let your answer _only_ include the actual code, not like: 'Sure, here's an idea with etc.etc' ?

Also, give the entire code in one single code please, don't structure your code output in different JSON objects. don't forget to include all the imports, the setups, etc.
Also, please format the code so that i can execute it using: exec(your_output)
"""


API_KEY = "AIzaSyDW1O0KiCJaS_Q7Rf4l3iRiemBE9YGOKW4"
URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

headers = {
    "Content-Type": "application/json",
    "x-goog-api-key": API_KEY
}

payload = {
    "contents": [
        {
            "parts": [
                {"text": code + prompt}
            ]
        }
    ],
    "generationConfig": {
        "response_mime_type": "application/json"
    }
}

response = requests.post(URL, headers=headers, data=json.dumps(payload))

# Parse and print the JSON response
if response.status_code == 200:
    result = response.json()
    #print(json.dumps(result, indent=2))
else:
    print(f"Error {response.status_code}: {response.text}")

code = result["candidates"][0]["content"]["parts"][0]["text"]
print(code)

try: exec(str(code))
except Exception as e:
    print(e)
