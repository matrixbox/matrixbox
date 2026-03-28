from fetch_data import fetch
#from load_settings import savesettings
from __main__ import *
import __main__
#from main import connect_to_network
#import __main__
#print(dir(__main__))
exitbutton = """<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><style>body{background:#0d0d12;color:#e8e8f0;font-family:system-ui,sans-serif;display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:100vh;gap:16px;margin:0}a.xbtn{display:inline-flex;align-items:center;gap:8px;padding:12px 28px;border-radius:12px;background:linear-gradient(135deg,#ff4b4b,#ff7070);color:#fff;font-weight:700;font-size:1rem;text-decoration:none}.lbl{color:#888;font-size:.8rem;text-transform:uppercase;letter-spacing:1.5px}</style></head><body><p class="lbl">App Running</p><a class="xbtn" href="/exit">&#x2715; Exit App</a>"""
backbutton = """<a class="back-btn" href="../">&#8592; Back</a>"""
bootloaderbutton = """<button class="btn btn-danger" onclick="if(confirm('Enter bootloader mode?'))fetch('/bootloader',{method:'POST'})">&#x26A1; Bootloader</button>"""
#unlock = """<button class="center" onclick="window.location.href='/unlock'" style='background-color:yellow'> &#128275; </button>"""
unlock = """<button class="btn btn-warning" onclick="fetch('/?unlock=true', {method: 'POST'})">&#x1F513; Unlock</button>"""

def _get_installed_apps():
    apps = []
    for app in os.listdir():
        if app == "LICENSE": continue
        if not "." in app:
            if not "__init__.py" in os.listdir(app): continue
            apps.append(app)
    return apps

def _dir_size(path):
    total = 0
    try:
        for f in os.listdir(path):
            fp = path + "/" + f
            try:
                s = os.stat(fp)
                if s[0] & 0x4000:  # directory
                    total += _dir_size(fp)
                else:
                    total += s[6]
            except: pass
    except: pass
    return total

def _fmt_size(b):
    if b < 1024: return str(b) + " B"
    elif b < 1024*1024: return str(b // 1024) + " KB"
    else: return "{:.1f} MB".format(b / (1024*1024))

def _free_space():
    s = os.statvfs("/")
    return s[0] * s[3]  # block size * free blocks

def textbox(settings):
    slider_cfg = {
        "wifi_power": {"min": 7, "max": 20, "step": 1},
        "rotation": {"min": 0, "max": 270, "step": 90},
        "width": {"min": 64, "max": 640, "step": 64},
        "height": {"min": 32, "max": 320, "step": 32},
    }
    advanced_keys = {"width", "height", "tiles", "repository_url"}
    advanced_order = ["width", "height", "tiles", "repository_url"]
    main_html = ""
    adv_items = {}
    settings_html = """<form action="/" method="POST">"""
    for setting in settings:
        print("Setting: ", setting)
        val = settings[setting]
        is_adv = setting in advanced_keys
        chunk = ""
        if setting == "autostart":
            apps = _get_installed_apps()
            checked = "checked" if val else ""
            disabled = "" if val else "disabled"
            opts = ""
            for a in apps:
                sel = "selected" if str(val) == a else ""
                opts += f'<option value="{a}" {sel}>{a}</option>'
            chunk = f"""<label>{setting}</label>
<div class="toggle-row">
<input type="checkbox" id="as_chk" {checked} onchange="var s=document.getElementById('as_sel');var h=document.getElementById('autostart');s.disabled=!this.checked;if(!this.checked){{s.value='';h.value='';}}">
<label for="as_chk">Enable autostart</label>
</div>
<input type="hidden" id="autostart" name="autostart" value="{val if val else ''}">
<select id="as_sel" {disabled} onchange="document.getElementById('autostart').value=this.value"><option value="">-- none --</option>{opts}</select>"""
        elif setting == "screensaver":
            apps = _get_installed_apps()
            checked = "checked" if val else ""
            disabled = "" if val else "disabled"
            opts = ""
            for a in apps:
                sel = "selected" if str(val) == a else ""
                opts += f'<option value="{a}" {sel}>{a}</option>'
            chunk = f"""<label>{setting}</label>
<div class="toggle-row">
<input type="checkbox" id="ss_chk" {checked} onchange="var s=document.getElementById('ss_sel');var h=document.getElementById('screensaver');s.disabled=!this.checked;if(!this.checked){{s.value='';h.value='';}}">
<label for="ss_chk">Enable screensaver</label>
</div>
<input type="hidden" id="screensaver" name="screensaver" value="{val if val else ''}">
<select id="ss_sel" {disabled} onchange="document.getElementById('screensaver').value=this.value"><option value="">-- none --</option>{opts}</select>"""
        elif setting in slider_cfg:
            c = slider_cfg[setting]
            try: cur = int(float(val))
            except: cur = c["min"]
            if setting == "rotation":
                chunk = f"""<label>{setting}</label>
<div class="range-wrap">
<input type="range" id="{setting}" name="{setting}" min="{c['min']}" max="{c['max']}" step="{c['step']}" value="{cur}" oninput="document.getElementById('v_{setting}').textContent=this.value" onchange="fetch('/rotate?v='+this.value,{{method:'POST'}})">
<span class="range-val" id="v_{setting}">{cur}</span>
</div>"""
            else:
                chunk = f"""<label>{setting}</label>
<div class="range-wrap">
<input type="range" id="{setting}" name="{setting}" min="{c['min']}" max="{c['max']}" step="{c['step']}" value="{cur}" oninput="document.getElementById('v_{setting}').textContent=this.value">
<span class="range-val" id="v_{setting}">{cur}</span>
</div>"""
        else:
            chunk = f"""<label for="{setting}">{setting}</label>
<input type="text" id="{setting}" name="{setting}" placeholder="{str(val)}">"""
        if is_adv:
            adv_items[setting] = chunk
        else:
            main_html += chunk
    settings_html += main_html
    adv_html = "".join(adv_items[k] for k in advanced_order if k in adv_items)
    if adv_html:
        settings_html += """<div style="margin-top:12px"><button type="button" class="btn btn-sm" onclick="var a=document.getElementById('adv_section');a.style.display=a.style.display==='none'?'block':'none'">&#9881; Advanced</button></div><div id="adv_section" style="display:none">""" + adv_html + """</div>"""
    return settings_html + """<button class="btn btn-full" type="submit">Save Settings</button></form>"""
    
def _draw_progress(current, total, filename, error=False, label="installing"):
    from load_screen import window, pset, font_mini
    w = display.width
    h = display.height
    window.fill(0)
    # Draw filename on line 1 first (line=1 does NOT auto-refresh)
    name = filename.split("/")[-1]
    pprint(name, 1, _clearscreen=False, color="yellow" if not error else "red")
    # Draw progress bar (no refresh yet)
    bar_h = 4
    bar_y = h - bar_h - 9
    bar_x = 1
    bar_w = w - 2
    for px in range(bar_x, bar_x + bar_w):
        pset(px, bar_y, 5)
        pset(px, bar_y + bar_h, 5)
    for py in range(bar_y, bar_y + bar_h + 1):
        pset(bar_x, py, 5)
        pset(bar_x + bar_w - 1, py, 5)
    fill_w = int((bar_w - 2) * current / max(total, 1))
    for px in range(bar_x + 1, bar_x + 1 + fill_w):
        for py in range(bar_y + 1, bar_y + bar_h):
            pset(px, py, 7)
    # Draw label on line 0 LAST (line=0 auto-refreshes, showing complete frame)
    pprint(label + " " + str(current) + "/" + str(total), 0, _clearscreen=False)

def install_app(app):
    if app == "system": app = "/"
    print("Install: ", app)
    applist = load_settings.latest_available_apps
    no_of_files = len(applist[app])
    print("Applist: ", applist, " Files: ", no_of_files)
    os.chdir("/")
    if app != "/":
        try: os.mkdir(app)
        except: pass
        try: os.chdir(app)
        except: pass
    error_color = "green"
    from load_screen import window
    try:
        microcontroller.cpu.frequency = 240000000
        clearscreen(False)
        # Pass 1: download all files, verify each returns 200
        downloads = []
        for x, file in enumerate(applist[app]):
            if "/" in file:
                parts = file.split("/")[:-1]
                path = ""
                for part in parts:
                    path = path + "/" + part if path else part
                    try: os.mkdir(path)
                    except: pass
            print("File: ", file)
            file_url = settings["repository_url"]
            if app != "/": file_url += app + "/"
            _draw_progress(x, no_of_files, file)
            resp = requests.get(file_url + file)
            print(resp.status_code)
            if resp.status_code != 200:
                _draw_progress(x + 1, no_of_files, file, True)
                try: resp.close()
                except: pass
                pprint("http " + str(resp.status_code), color="red", line=-1, _refresh=True)
                return
            if ".mpy" in file:
                downloads.append((file, bytearray(resp.content), "wb"))
            else:
                downloads.append((file, resp.text, "w"))
            _draw_progress(x + 1, no_of_files, file)
        # Pass 2: all downloads OK, write to disk
        window.fill(0)
        display.refresh()
        for fname, data, mode in downloads:
            try:
                with open(str(fname), mode) as f: f.write(data)
            except:
                error_color = "red"
        downloads = None
        #gc.collect()
    finally:
        microcontroller.cpu.frequency = 180000000
        os.chdir("/")
        window.fill(0)
        pprint("Done.", 1, _clearscreen=True)
        __main__.show_logo()
        


def _repo_api_base():
    """Derive GitHub API repo path from repository_url.
    e.g. 'https://raw.githubusercontent.com/matrixbox/matrixbox/refs/heads/main/'
    -> owner='matrixbox', repo='matrixbox'
    """
    url = settings["repository_url"]
    parts = url.replace("https://", "").split("/")
    return parts[1], parts[2]

def get_updates():
    print(settings)
    try:
        owner, repo = _repo_api_base()
        url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/main?recursive=1"
        resp = requests.get(url, headers={"User-Agent": "MatrixBox"})
        tree = json.loads(resp.text)["tree"]
        resp.close()
        apps = {}
        root_files = []
        for item in tree:
            if item["type"] != "blob": continue
            path = item["path"]
            parts = path.split("/")
            if len(parts) == 1:
                root_files.append(parts[0])
                continue
            dirname = parts[0]
            filename = "/".join(parts[1:])
            if dirname not in apps: apps[dirname] = []
            apps[dirname].append(filename)
        # System = root files + lib folder
        system_files = root_files[:]
        if "lib" in apps:
            for f in apps["lib"]:
                system_files.append("lib/" + f)
        apps["/"] = system_files
        # Keep only dirs with __init__.py, "lib", or root "/"
        apps = {k: v for k, v in apps.items() if k in ("/", "lib") or "__init__.py" in v}
    except Exception as e:
        print("get_updates error:", e)
        apps = {}
    return apps
    
def list_available_apps(apps):
    print("Apps: ", apps)
    load_settings.latest_available_apps = apps
    applist = """<div class="download-item">
    <span class="download-name">&#x1F4E6; System</span>
    <button class="btn btn-sm btn-warning" onclick="installsystem()">&#x21BB; Update</button>
    <script>function installsystem() {
    fetch("/?install=system", { method: "POST" }).then(() => {
        setTimeout(() => { window.location.href = "/download"; }, 10);
    });}</script></div>"""

    for dir in apps:
        if dir == "/" or dir == "lib": continue
        if dir in os.listdir() and "__init__.py" in os.listdir(dir):
            sz = _fmt_size(_dir_size(dir))
            applist += f'<div class="download-item"><div><span class="download-name">&#x2713; {dir}</span><div style="font-size:.7rem;color:var(--muted);margin-top:2px">{sz}</div></div>' + """<button class="btn btn-sm btn-danger" onclick="delete"""+dir+"""()">Delete</button>
<script>function delete"""+dir+"""() {
    fetch("/?delete="""+dir+"""", { method: "POST" }).then(() => {
        setTimeout(() => { window.location.href = "/download"; }, 10);
    });}</script></div>"""
        else:
            applist += f'<div class="download-item"><span class="download-name">{dir}</span>' + """<button class="btn btn-sm btn-success" onclick="install"""+dir+"""()">&#x2B07; Install</button>
<script>function install"""+dir+"""() {
    fetch("/?install="""+dir+"""", { method: "POST" }).then(() => {
        setTimeout(() => { window.location.href = "/download"; }, 10);
    });}</script></div>"""
    return applist


def latest_wifi_error():
    return str(__main__.wifi_status)

def css():
    return """
:root{--bg:#0d0d12;--surface:#18181f;--surface2:#22223a;--accent:#6c63ff;--accent2:#00bfff;--text:#e8e8f0;--muted:#888899;--border:rgba(255,255,255,.07);--r:12px;--r-lg:18px}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--text);font-family:'Segoe UI',system-ui,-apple-system,sans-serif;min-height:100vh;padding-bottom:32px}
.navbar{position:sticky;top:0;z-index:100;background:var(--surface);border-bottom:1px solid var(--border);padding:0 12px;display:flex;align-items:center;height:44px;gap:6px;backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px)}
.nav-brand{font-weight:800;font-size:.95rem;background:linear-gradient(135deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-right:8px;text-decoration:none}
.nav-link{color:var(--muted);text-decoration:none;font-size:.78rem;padding:6px 10px;border-radius:8px;transition:color .2s,background .2s;font-weight:500}
.nav-link:hover{color:var(--text);background:var(--surface2)}
.nav-spacer{flex:1}
.nav-info{color:var(--muted);font-size:.7rem;letter-spacing:.3px;text-align:right;line-height:1.3}
.nav-info span{display:block}
.nav-x{color:#ff5555;font-size:1.1rem;font-weight:700;text-decoration:none;width:30px;height:30px;display:flex;align-items:center;justify-content:center;border-radius:8px;transition:background .2s;margin-left:6px}
.nav-x:hover{background:rgba(255,85,85,.15)}
.page{max-width:480px;margin:0 auto;padding:16px}
.logo{text-align:center;padding:28px 0 20px}
.logo h1{font-size:1.9rem;font-weight:800;background:linear-gradient(135deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;letter-spacing:-.5px}
.logo p{color:var(--muted);font-size:.85rem;margin-top:5px}
.card{background:var(--surface);border:1px solid var(--border);border-radius:var(--r-lg);padding:18px;margin-bottom:12px}
.section-title{font-size:.7rem;color:var(--muted);text-transform:uppercase;letter-spacing:1.2px;font-weight:700;margin-bottom:12px}
.app-item,.download-item{display:flex;align-items:center;justify-content:space-between;padding:11px 0;border-bottom:1px solid var(--border)}
.app-item:last-child,.download-item:last-child{border-bottom:none}
.app-name,.download-name{font-size:.95rem;font-weight:500;text-transform:capitalize;color:var(--text)}
label{display:block;font-size:.7rem;color:var(--muted);text-transform:uppercase;letter-spacing:.8px;margin:14px 0 5px;font-weight:600}
input[type="text"],select{width:100%;background:var(--surface2);border:1.5px solid var(--border);border-radius:var(--r);padding:10px 13px;color:var(--text);font-size:.95rem;outline:none;transition:border-color .2s;-webkit-appearance:none}
input[type="text"]:focus,select:focus{border-color:var(--accent)}
select option{background:var(--surface2)}
.range-wrap{display:flex;align-items:center;gap:10px;margin-top:4px}
.range-wrap input[type="range"]{flex:1;-webkit-appearance:none;appearance:none;height:6px;border-radius:3px;background:var(--surface2);outline:none}
.range-wrap input[type="range"]::-webkit-slider-thumb{-webkit-appearance:none;width:20px;height:20px;border-radius:50%;background:linear-gradient(135deg,var(--accent),var(--accent2));cursor:pointer;border:2px solid var(--bg)}
.range-val{min-width:36px;text-align:center;font-size:.88rem;font-weight:700;color:var(--accent2);background:var(--surface2);padding:4px 8px;border-radius:8px}
.toggle-row{display:flex;align-items:center;gap:10px;margin:10px 0}
.toggle-row input[type="checkbox"]{width:18px;height:18px;accent-color:var(--accent)}
.toggle-row label{margin:0;font-size:.85rem;color:var(--text);text-transform:none;letter-spacing:0;font-weight:500}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:6px;padding:9px 18px;border:none;border-radius:var(--r);font-size:.88rem;font-weight:600;cursor:pointer;transition:opacity .15s,transform .1s;color:#fff;background:linear-gradient(135deg,var(--accent),var(--accent2));text-decoration:none}
.btn:hover{opacity:.85;transform:translateY(-1px)}
.btn:active{transform:translateY(0);opacity:1}
.btn-sm{padding:7px 13px;font-size:.82rem}
.btn-full{width:100%;padding:12px;font-size:.95rem;margin-top:10px}
.btn-danger{background:linear-gradient(135deg,#ff4b4b,#ff7070)}
.btn-success{background:linear-gradient(135deg,#00c85d,#00e676);color:#000}
.btn-warning{background:linear-gradient(135deg,#f5a623,#f8ca55);color:#111}
.btn-ghost{background:var(--surface2);border:1px solid var(--border);color:var(--text)}
.btn-ghost:hover{border-color:var(--accent)}
.action-row{display:flex;gap:10px;flex-wrap:wrap}
.back-btn{display:inline-flex;align-items:center;gap:6px;color:var(--muted);text-decoration:none;font-size:.85rem;padding:8px 14px;border-radius:var(--r);background:var(--surface);border:1px solid var(--border);margin-top:14px;transition:color .2s,border-color .2s}
.back-btn:hover{color:var(--text);border-color:var(--accent)}
.error-msg{color:#ff7070;font-size:.82rem;margin-top:10px;text-align:center}
"""

def navbar():
    ip = str(wifi.radio.ipv4_address) if wifi.radio.ipv4_address else "OFFLINE"
    return f"""<nav class="navbar">
<a class="nav-brand" href="http://matrixbox.io">MatrixBox</a>
<a class="nav-link" href="/">Apps</a>
<a class="nav-link" href="/download">Store</a>
<a class="nav-link" href="/settings">Settings</a>
<div class="nav-spacer"></div>
<div class="nav-info"><span id="clk"></span><span>{ip}</span></div>
<button class="nav-x" onclick="if(confirm('Restart?'))fetch('/reset',{{method:'POST'}})" title="Restart">&#x2715;</button>
</nav>
<script>function _ck(){{var d=new Date(),h=d.getHours(),m=d.getMinutes();document.getElementById('clk').textContent=(h<10?'0':'')+h+':'+(m<10?'0':'')+m;}}_ck();setInterval(_ck,15000);</script>"""

def header(title="Settings"):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>{css()}</style>
</head>
<body>{navbar()}<div class="page">"""

def footer(back=False):
    back_html = backbutton if back else ""
    return f"""{back_html}</div></body></html>"""

def connect_to_wifi():
    def scan():
        networks = ""
        for network in wifi.radio.start_scanning_networks(start_channel=1, stop_channel=14):
            networks += f"<option value='{network.ssid}' data-ch='{network.channel}'>{network.ssid} (ch {network.channel})</option>"
            print(network.ssid, "ch", network.channel)
        wifi.radio.stop_scanning_networks()
        return networks
    networks = scan()
    wifi_error = latest_wifi_error()
    error_html = f'<p class="error-msg">{wifi_error}</p>' if wifi_error else ""
    return header("Connect to WiFi") + f"""<div class="logo">
    <h1>WiFi Setup</h1>
    <p>Connect to a wireless network</p>
</div>
<div class="card">
    <label for="ssid">Network</label>
    <select id="ssid" name="ssid">{networks}</select>
    <script>
    var _ssid = document.getElementById("ssid");
    function _sendSSID(el) {{
        var opt = el.options[el.selectedIndex];
        var v = opt.value.replace(/#/g, "%23");
        var ch = opt.getAttribute("data-ch") || "";
        fetch("/?ssid=" + v + "&channel=" + ch, {{ method: "POST" }});
    }}
    _ssid.addEventListener("change", function() {{ _sendSSID(_ssid); }});
    _ssid.addEventListener("click",  function() {{ _sendSSID(_ssid); }});
    </script>
    <label for="password">Password</label>
    <input type="text" id="password" name="password" placeholder="Enter password">
    <script>
    document.getElementById("password").addEventListener("blur", function(e) {{
        var p = e.target.value.replace(/#/g, "%23");
        fetch("/?password=" + encodeURIComponent(p), {{ method: "POST" }});
    }});
    </script>
    <button class="btn btn-full" onclick="location.href='/connect'">Connect</button>
    {error_html}
</div>""" + footer()

def select_app():
    installed_apps = ""
    for app in os.listdir():
        if app == "LICENSE": continue
        if not "." in app:
            if not "__init__.py" in os.listdir(app): continue
            installed_apps += f'<div class="app-item"><span class="app-name">{app}</span>' + """<button class="btn btn-sm" onclick="run"""+app+"""()">&#9654; Run</button>
<script>function run"""+app+"""() {
    fetch("/?run="""+app+"""", { method: "GET" }).then(() => {
        setTimeout(() => { window.location.href = "/"; }, 10);
    });}</script></div>"""
    if not installed_apps:
        installed_apps = '<p style="color:var(--muted);text-align:center;padding:20px 0;font-size:.9rem">No apps installed yet</p>'
    return header("MatrixBox") + """<div class="logo">
    <h1>MatrixBox</h1>
    <p>Select an app to launch</p>
</div>
<div class="card">
    <div class="section-title">Installed Apps</div>
    """ + installed_apps + """
</div>
<button class="btn btn-full" onclick="window.location.href='/download'">&#x2B07; Download Apps</button>
<button class="btn btn-full btn-ghost" onclick="window.location.href='/settings'">&#9881; Settings</button>
<div class="card" style="margin-top:10px;border:1px dashed var(--muted)">
    <div class="section-title" style="color:var(--muted)">Built-in Tools</div>
    <div class="app-item"><span class="app-name" style="color:var(--muted)">&#x1F4BB; Terminal</span><button class="btn btn-sm" style="background:var(--muted);color:var(--bg)" onclick="window.location.href='/cmd'">Open</button></div>
</div>
""" + footer()

@ampule.route('/settingsx')
def _settings(request):
    global settings
    print(__main__.settings)
    return (200, {}, str(settings))

@ampule.route('/connect')
def _connect(request):
    clearscreen()
    print(connect_to_network())
    return (200, {}, """<meta http-equiv="refresh" content="0; url=../" />""")

@ampule.route('/connectx')
def _connectx(request):
    return (200, {}, select_app() + connect_to_wifi())

@ampule.route('/', method="POST")
def webinterface_post(request):
    global settings
    print("POSTED! ", request.params)
    try:
        pairs = request.body.split('&')
        parsed_data = {}
        for pair in pairs:
            key, value = pair.split('=')
            parsed_data[key] = url_decoder(value)
        request.params = parsed_data
        print(parsed_data)
        print("POSTED body:", request.body)
        for setting in parsed_data:
            if parsed_data[setting] or setting in ("autostart", "screensaver"):
                try:
                    val = parsed_data[setting]
                    if setting in settings and isinstance(settings[setting], int):
                        val = int(val)
                    settings[setting] = val
                except: pass
        clearscreen(True)
        savesettings(settings)
        clearscreen(False)
        __main__.autostart = settings.get("autostart", False)
        __main__.screensaver_app = settings.get("screensaver", "")
        try: apply_display_settings()
        except Exception as e: print("apply_display_settings:", e)
        return (200, {}, """<meta http-equiv="refresh" content="0; url=../" />""")
    except: pass

    try: 
        if "unlock" in request.params:
            try: 
                with open("unlock","w") as f: f.write("")
            except: pass
            import safemode
        if "ssid" in request.params:
            __main__.settings["ssid"] = url_decoder(request.params["ssid"])
        if "channel" in request.params:
            try: __main__.settings["channel"] = int(request.params["channel"])
            except: pass
        if "password" in request.params:
            __main__.settings["password"] = url_decoder(request.params["password"])
            #wifi.radio.connect(settings["ssid"], settings["password"])
        if "delete" in request.params:
            dir = request.params["delete"]
            error_color = "green"
            try:
                os.chdir(dir)
                files = os.listdir()
                total = len(files)
                clearscreen(False)
                for x, file in enumerate(files):
                    _draw_progress(x, total, file, label="deleting")
                clearscreen(True)
                for x, file in enumerate(files):
                    try:
                        os.remove(file)
                    except Exception as e:
                        error_color = "red"
                        print(e)
                clearscreen(False)
                _draw_progress(total, total, files[-1] if files else "", error_color == "red", label="deleting")
            finally:
                os.chdir("/")
            try: os.rmdir(dir)
            except: pass
            pprint("done!", color=error_color, line=-1, _refresh=True)
        if "install" in request.params:
            print(request.params["install"])
            install_app(request.params["install"])
    except Exception as e: print(e)
    return (200, {}, """<meta http-equiv="refresh" content="0; url=../" />""")

@ampule.route('/bootloader', method='POST')
def bootloader(request):
    import microcontroller
    microcontroller.on_next_reset(microcontroller.RunMode.BOOTLOADER)
    microcontroller.reset()
    return (200, {}, "None")

@ampule.route("/preset", method='POST')
def _preset(request):
    presets = {"xs": (64, 32), "x": (128, 32), "xl": (192, 32), "2x": (128, 64)}
    if request.params and "s" in request.params:
        p = request.params["s"]
        if p in presets:
            w, h = presets[p]
            settings["width"] = w
            settings["height"] = h
            settings["tiles"] = 1
            try: load_settings.savesettings(settings)
            except: pass
            microcontroller.reset()
    return (200, {}, "")

@ampule.route("/rotate", method='POST')
def _rotate(request):
    if request.params and "v" in request.params:
        new_r = int(request.params["v"])
    else:
        new_r = (display.rotation + 90) % 360
    settings["rotation"] = new_r
    display.rotation = new_r
    clearscreen(lines=True)
    try: __main__.show_logo()
    except:
        pprint("Rotated: " + str(new_r), line=0)
        pprint(str(display.width) + "x" + str(display.height))
    return (200, {}, "")

@ampule.route("/settings")
def _settings(request):
    global settings
    rotate_btn = '<button class="btn btn-sm" onclick="fetch(\'/rotate\',{method:\'POST\'}).then(()=>{{var v=document.getElementById(\'v_rotation\');if(v){{var c=parseInt(v.textContent)||0;c=(c+90)%360;v.textContent=c;var s=document.getElementById(\'rotation\');if(s)s.value=c;}}}});">&#128260; 90&deg;</button>'
    preset_btns = ''.join([
        '<button class="btn btn-sm" onclick="if(confirm(\'Switch to XS (64x32)? Device will reboot.\'))fetch(\'/preset?s=xs\',{method:\'POST\'})" title="XS 64x32"><svg width="20" height="16" viewBox="0 0 20 16"><rect x="4" y="4" width="12" height="8" rx="1" fill="black" stroke="currentColor" stroke-width="1.5"/></svg><br><span style="font-size:.6rem">XS</span></button>',
        '<button class="btn btn-sm" onclick="if(confirm(\'Switch to X (128x32)? Device will reboot.\'))fetch(\'/preset?s=x\',{method:\'POST\'})" title="X 128x32"><svg width="28" height="16" viewBox="0 0 28 16"><rect x="2" y="4" width="24" height="8" rx="1" fill="black" stroke="currentColor" stroke-width="1.5"/></svg><br><span style="font-size:.6rem">X</span></button>',
        '<button class="btn btn-sm" onclick="if(confirm(\'Switch to XL (192x32)? Device will reboot.\'))fetch(\'/preset?s=xl\',{method:\'POST\'})" title="XL 192x32"><svg width="36" height="16" viewBox="0 0 36 16"><rect x="2" y="4" width="32" height="8" rx="1" fill="black" stroke="currentColor" stroke-width="1.5"/></svg><br><span style="font-size:.6rem">XL</span></button>',
        '<button class="btn btn-sm" onclick="if(confirm(\'Switch to 2X (128x64)? Device will reboot.\'))fetch(\'/preset?s=2x\',{method:\'POST\'})" title="2X 128x64"><svg width="24" height="18" viewBox="0 0 24 18"><rect x="2" y="1" width="20" height="16" rx="1" fill="black" stroke="currentColor" stroke-width="1.5"/></svg><br><span style="font-size:.6rem">2X</span></button>',
    ])
    settings_html = header("Settings") + """<div class="logo"><h1>Settings</h1><p>Configure your device</p></div>
<div class="card"><div class="section-title">Quick Actions</div><div class="action-row">""" + rotate_btn + preset_btns + """</div></div>
<div class="card"><div class="section-title">Device Settings</div>""" + f"""{textbox(settings)}</div>

<div class="card action-row">""" + bootloaderbutton + " " + unlock + """</div>""" + footer(True)
    return (200, {}, settings_html)

@ampule.route("/save", method='POST')
def _save(request):
    global settings
    try: load_settings.savesettings(settings)
    except: print("Failed to save!")
    return (200, {}, '{"ok":true}')

@ampule.route('/download')
def download(request):
    free = _fmt_size(_free_space())
    content = """<div class="logo"><h1>App Store</h1><p>Install or update apps</p></div>
<div class="card" style="text-align:center;padding:12px"><span style="font-size:.8rem;color:var(--muted)">Available space: </span><span style="font-size:.9rem;font-weight:700;color:var(--accent2)">""" + free + """</span></div>
<div class="card"><div class="section-title">Available</div>""" + str(list_available_apps(get_updates())) + """</div>"""
    return (200, {}, header("Download apps") + content + footer(True))


####################################################
# DEBUG FUNKTIONER
####################################################

import cmd


@ampule.route("/settingsx")
def showsettings(request):
    return (200, {}, str(settings))

@ampule.route('/reset', method='POST')
def reset(request): microcontroller.reset()


def url_decoder(url):
    url_decode = {"%C3A4":"ä", "%20": " ", "%21": "!", "%22": "\"", "%23": "#", "%24": "$", "%25": "%", "%26": "&", "%27": "'", "%28": "(", "%29": ")", "%2A": "*", "%2B": "+", "%2C": ",", "%2D": "-", "%2E": ".", "%2F": "/", "%30": "0", "%31": "1", "%32": "2", "%33": "3", "%34": "4", "%35": "5", "%36": "6", "%37": "7", "%38": "8", "%39": "9", "%3A": ":", "%3B": ";", "%3C": "<", "%3D": "=", "%3E": ">", "%3F": "?", "%40": "@", "%41": "A", "%42": "B", "%43": "C", "%44": "D", "%45": "E", "%46": "F", "%47": "G", "%48": "H", "%49": "I", "%4A": "J", "%4B": "K", "%4C": "L", "%4D": "M", "%4E": "N", "%4F": "O", "%50": "P", "%51": "Q", "%52": "R", "%53": "S", "%54": "T", "%55": "U", "%56": "V", "%57": "W", "%58": "X", "%59": "Y", "%5A": "Z", "%5B": "[", "%5C": "\\", "%5D": "]", "%5E": "^", "%5F": "_", "%60": "`", "%61": "a", "%62": "b", "%63": "c", "%64": "d", "%65": "e", "%66": "f", "%67": "g", "%68": "h", "%69": "i", "%6A": "j", "%6B": "k", "%6C": "l", "%6D": "m", "%6E": "n", "%6F": "o", "%70": "p", "%71": "q", "%72": "r", "%73": "s", "%74": "t", "%75": "u", "%76": "v", "%77": "w", "%78": "x", "%79": "y", "%7A": "z", "%7B": "{", "%7C": "|", "%7D": "}", "%7E": "~", "%E2%82%AC": "\u20ac", "%E2%80%9A": "\u201a", "%C6%92": "\u0192", "%E2%80%9E": "\u201e", "%E2%80%A6": "\u2026", "%E2%80%A0": "\u2020", "%E2%80%A1": "\u2021", "%CB%86": "\u02c6", "%E2%80%B0": "\u2030", "%C5%A0": "\u0160", "%E2%80%B9": "\u2039", "%C5%92": "\u0152", "%C5%BD": "\u017d", "%E2%80%98": "\u2018", "%E2%80%99": "\u2019", "%E2%80%9C": "\u201c", "%E2%80%9D": "\u201d", "%E2%80%A2": "\u2022", "%E2%80%93": "\u2013", "%E2%80%94": "\u2014", "%CB%9C": "\u02dc", "%E2%84": "\u2122", "%C5%A1": "\u0161", "%E2%80": "\u203a", "%C5%93": "\u0153", "%C5%B8": "\u0178", "%C2%A1": "\u00a1", "%C2%A2": "\u00a2", "%C2%A3": "\u00a3", "%C2%A4": "\u00a4", "%C2%A5": "\u00a5", "%C2%A6": "\u00a6", "%C2%A7": "\u00a7", "%C2%A8": "\u00a8", "%C2%A9": "\u00a9", "%C2%AA": "\u00aa", "%C2%AB": "\u00ab", "%C2%AD": "\u00ac", "%C2%AE": "\u00ae", "%C2%AF": "\u00af", "%C2%B0": "\u00b0", "%C2%B1": "\u00b1", "%C2%B2": "\u00b2", "%C2%B3": "\u00b3", "%C2%B4": "\u00b4", "%C2%B5": "\u00b5", "%C2%B6": "\u00b6", "%C2%B7": "\u00b7", "%C2%B8": "\u00b8", "%C2%B9": "\u00b9", "%C2%BA": "\u00ba", "%C2%BB": "\u00bb", "%C2%BC": "\u00bc", "%C2%BD": "\u00bd", "%C2%BE": "\u00be", "%C2%BF": "\u00bf", "%C3%80": "\u00c0", "%C3%81": "\u00c1", "%C3%82": "\u00c2", "%C3%83": "\u00c3", "%C3%84": "\u00c4", "%C3%85": "\u00c5", "%C3%86": "\u00c6", "%C3%87": "\u00c7", "%C3%88": "\u00c8", "%C3%89": "\u00c9", "%C3%8A": "\u00ca", "%C3%8B": "\u00cb", "%C3%8C": "\u00cc", "%C3%8D": "\u00cd", "%C3%8E": "\u00ce", "%C3%8F": "\u00cf", "%C3%90": "\u00d0", "%C3%91": "\u00d1", "%C3%92": "\u00d2", "%C3%93": "\u00d3", "%C3%94": "\u00d4", "%C3%95": "\u00d5", "%C3%96": "\u00d6", "%C3%97": "\u00d7", "%C3%98": "\u00d8", "%C3%99": "\u00d9", "%C3%9A": "\u00da", "%C3%9B": "\u00db", "%C3%9C": "\u00dc", "%C3%9D": "\u00dd", "%C3%9E": "\u00de", "%C3%9F": "\u00df", "%C3%A0": "\u00e0", "%C3%A1": "\u00e1", "%C3%A2": "\u00e2", "%C3%A3": "\u00e3", "%C3%A4": "\u00e4", "%C3%A5": "\u00e5", "%C3%A6": "\u00e6", "%C3%A7": "\u00e7", "%C3%A8": "\u00e8", "%C3%A9": "\u00e9", "%C3%AA": "\u00ea", "%C3%AB": "\u00eb", "%C3%AC": "\u00ec", "%C3%AD": "\u00ed", "%C3%AE": "\u00ee", "%C3%AF": "\u00ef", "%C3%B0": "\u00f0", "%C3%B1": "\u00f1", "%C3%B2": "\u00f2", "%C3%B3": "\u00f3", "%C3%B4": "\u00f4", "%C3%B5": "\u00f5", "%C3%B6": "\u00f6", "%C3%B7": "\u00f7", "%C3%B8": "\u00f8", "%C3%B9": "\u00f9", "%C3%BA": "\u00fa", "%C3%BB": "\u00fb", "%C3%BC": "\u00fc", "%C3%BD": "\u00fd", "%C3%BE": "\u00fe", "%C3%BF": "\u00ff", 
"%C4%8C":"\u010c",
"%C4%86":"\u0106",
"%C5%BD":"\u017d",
"%C4%90":"\u0110",
"%C5%A0":"\u0160",
"%C4%8D":"\u010d",
"%C4%87":"\u0107",
"%C5%BE":"\u017e",
"%C4%91":"\u0111",
"%C5%A1":"\u0161",
"%E2%82%BF":"₿"}

    for char in url_decode: url = url.replace(char, url_decode[char])
    return url

