from __main__ import *
import sys, time, random
import load_screen
from check_button import check_if_button_pressed
from load_screen import *
microcontroller.cpu.frequency = 240000000
import math, random

# Tuneable settings
fw_settings = {
    "particles": 75,
    "max_active": 3,
    "gravity": 10,
    "speed": 20,
    "lifetime": 30,
    "delay": 10,
}
try:
    with open("fwsettings.txt") as f:
        fw_settings.update(json.loads(f.read()))
except: pass

html = """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Fireworks</title><style>
body{background:#0d0d12;color:#e8e8f0;font-family:system-ui,sans-serif;max-width:420px;margin:0 auto;padding:16px}
h1{text-align:center;font-size:1.6rem;background:linear-gradient(135deg,#ff6b35,#ffd700);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.card{background:#18181f;border-radius:12px;padding:16px;margin:12px 0}
label{display:block;font-size:.85rem;color:#888;margin:10px 0 4px;text-transform:uppercase;letter-spacing:1px}
label:first-child{margin-top:0}
.range-wrap{display:flex;align-items:center;gap:10px}
input[type=range]{flex:1;accent-color:#6c63ff}
.val{min-width:28px;text-align:center;font-weight:700;font-size:.9rem}
.btn{display:block;width:100%;padding:12px;border:none;border-radius:10px;font-weight:700;font-size:1rem;cursor:pointer;margin-top:10px;text-align:center;text-decoration:none}
.btn-exit{background:linear-gradient(135deg,#ff4b4b,#ff7070);color:#fff}
</style></head><body>
<h1>&#127878; Fireworks</h1>
<div class="card">
<label>Particles per burst</label><div class="range-wrap"><input type="range" min="20" max="150" step="5" value="75" oninput="s('particles',this.value);this.nextElementSibling.textContent=this.value"><span class="val">75</span></div>
<label>Max simultaneous</label><div class="range-wrap"><input type="range" min="1" max="8" step="1" value="3" oninput="s('max_active',this.value);this.nextElementSibling.textContent=this.value"><span class="val">3</span></div>
<label>Gravity</label><div class="range-wrap"><input type="range" min="0" max="30" step="1" value="10" oninput="s('gravity',this.value);this.nextElementSibling.textContent=this.value"><span class="val">10</span></div>
<label>Speed</label><div class="range-wrap"><input type="range" min="5" max="50" step="1" value="20" oninput="s('speed',this.value);this.nextElementSibling.textContent=this.value"><span class="val">20</span></div>
<label>Lifetime</label><div class="range-wrap"><input type="range" min="10" max="80" step="5" value="30" oninput="s('lifetime',this.value);this.nextElementSibling.textContent=this.value"><span class="val">30</span></div>
<label>Launch delay</label><div class="range-wrap"><input type="range" min="1" max="30" step="1" value="10" oninput="s('delay',this.value);this.nextElementSibling.textContent=this.value"><span class="val">10</span></div>
</div>
<div style="display:flex;gap:10px"><button class="btn" style="background:linear-gradient(135deg,#6c63ff,#00bfff);color:#fff" onclick="fetch('/save').then(()=>this.textContent='\u2713 Saved!');setTimeout(()=>this.textContent='Save',1500)">Save</button></div>
<a class="btn btn-exit" href="/exit">&#x274C; Exit</a>
<script>function s(k,v){fetch('/set?k='+k+'&v='+v)}</script>
</body></html>"""

@ampule.route("/", method="GET")
def fireworks_interface(request):
    return (200, {}, html)

@ampule.route("/exit", method="GET")
def exit_webinterface(request):
    load_settings.app_running = False
    return (200, {}, """<meta http-equiv="refresh" content="0; url=../" />""")

@ampule.route("/set", method="GET")
def set_param(request):
    if request.params and "k" in request.params and "v" in request.params:
        k = request.params["k"]
        if k in fw_settings:
            fw_settings[k] = int(request.params["v"])
    return (200, {}, "ok")

@ampule.route("/save", method="GET")
def save_settings(request):
    try:
        with open("fwsettings.txt", "w") as f:
            f.write(json.dumps(fw_settings))
    except: pass
    return (200, {}, "ok")

width = display_width()
height = display_height()

def create_firework(x, y):
    particles = []
    num_particles = fw_settings["particles"]
    colors = [random.randint(1, 15) for _ in range(3)]
    spd = fw_settings["speed"] / 10.0
    lt = fw_settings["lifetime"]
    for _ in range(num_particles):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(0.3, spd)
        vx = speed * math.cos(angle)
        vy = speed * math.sin(angle)
        lifetime = random.randint(lt // 2, lt)
        color = random.choice(colors)
        particles.append({
            "x": x,
            "y": y,
            "vx": vx,
            "vy": vy,
            "lifetime": lifetime,
            "color": color
        })
    return particles

fireworks = []
last_firework_time = 0

while load_settings.app_running:
    current_time = time.monotonic()

    window.fill(0)

    # Create new fireworks randomly
    fw_delay = fw_settings["delay"] / 10.0
    if current_time - last_firework_time > fw_delay and len(fireworks) < fw_settings["max_active"]:
        x = random.randint(10, width - 10)
        y = random.randint(height // 4, height // 2)
        fireworks.append(create_firework(x, y))
        last_firework_time = current_time

    # Update and draw particles
    grav = fw_settings["gravity"] / 100.0
    new_fireworks = []
    for firework in fireworks:
        active_particles = []
        for particle in firework:
            particle["x"] += particle["vx"]
            particle["y"] += particle["vy"]
            particle["vy"] += grav

            particle["lifetime"] -= 1
            if particle["lifetime"] > 0 and 0 <= int(particle["x"]) < width and 0 <= int(particle["y"]) < height:
                pset(int(particle["x"]), int(particle["y"]), particle["color"])
                active_particles.append(particle)

        if active_particles:
            new_fireworks.append(active_particles)

    fireworks = new_fireworks

    refresh()
    ampule.listen(socket)

    b = check_if_button_pressed()
    if b: sys.exit()
