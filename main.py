
import sys, wifi, socketpool, time, os, json, microcontroller, ampule
import load_settings
import digitalio, board
import adafruit_connection_manager, adafruit_requests
settings =  load_settings.settings()
from load_screen import *
from check_button import *
pprint("^MatrixBox(", line=0, color="white", hr="¨")
pprint("^Matrix", line=0, color="brightwhite", _clearscreen=False)

wifi.radio.tx_power = 9.0
pool = socketpool.SocketPool(wifi.radio)
socket = pool.socket()
socket.setblocking(False)
socket.setsockopt(pool.SOL_SOCKET, pool.SO_REUSEADDR, 1)
socket.bind(('', 80))
socket.listen(5)
socket_timeout = 5
macid = "".join([hex(i) for i in wifi.radio.mac_address]).replace("0x","")[:8] # mac-id för hotspot
wifi_status = ""
ssl_context = adafruit_connection_manager.get_radio_ssl_context(wifi.radio)
requests = adafruit_requests.Session(pool, ssl_context)
first_start = True

def start_hotspot():
    try:
        wifi.radio.start_ap(ssid=macid)
        wifi.radio.start_dhcp_ap()
        pprint("Started WIFI: ")
        pprint(str(macid))
        pprint(str(wifi.radio.ipv4_address_ap))
    except Exception as e: pprint(str(e))

def connect_to_network(timeout=False, silent=False):
    global wifi_status
    wifi_status = ""
    print("Connecting...")
    try: 
        if not silent: pprint(str(settings["ssid"]))
        wifi.radio.connect(settings["ssid"],settings["password"], timeout=timeout)
        pprint(str(wifi.radio.ipv4_address))
    except Exception as e: 
        if not silent: pprint(str(e))
        wifi_status = str(e)
        print(e)
    return time.monotonic()

@ampule.route("/exit", method="GET")
def webinterface(request):
    load_settings.app_running = False
    return (200, {}, """<meta http-equiv="refresh" content="0; url=../" />""")

@ampule.route("/", method="GET")
def webinterface(request):
    if load_settings.app_running: 
        return (200, {}, str(exitbutton) + f"""<br> running app {load_settings.app_running}""")
    if request.params:
        if "run" in request.params: load_settings.app_running = request.params["run"]
    return (200, {}, select_app() + connect_to_wifi() if wifi.radio.connected == False else select_app())

def initialize_app():
    global autostart
    ampule_routes_backup = ampule.routes.copy()
    
    try: 
        clearscreen()
        pprint(f"Starting {load_settings.app_running}...")
        os.chdir(load_settings.app_running)
        time.sleep(0.5)
        import __init__
    except Exception as e: 
        pprint(f"{load_settings.app_running} crashed.")
        print(f"{e}")
        settings["autostart"] = 0
    finally: 
        microcontroller.cpu.frequency = 160000000
        autostart = False
        ampule.routes = ampule_routes_backup.copy()
        try: 
            for codefile in os.listdir():
                try: del sys.modules[codefile.replace(".py", "")]
                except: pass
            #del sys.modules["__init__"]
            #del sys.modules["code"]
        except: pass
        display.root_group = rf_group
        os.chdir("/")
        #clearscreen()
        pprint(str(wifi.radio.ipv4_address))
        pprint("Select app:")
        return False

def installed_apps():
    installed_apps = []
    for app in os.listdir():
        if not "." in app:
            if not "__init__.py" in os.listdir(app): continue
            installed_apps.append(app)
    return installed_apps if len(installed_apps) else ["No apps found"]

def next_program_in_list(run=False):
    try: load_settings.installed_apps_list[1]
    except: load_settings.installed_apps_list = installed_apps()
    if run:
        load_settings.app_running = load_settings.installed_apps_list[0]
        return
    print(load_settings.installed_apps_list)
    load_settings.installed_apps_list.append(load_settings.installed_apps_list[0])
    load_settings.installed_apps_list.pop(0)
    pprint(load_settings.installed_apps_list[0], line=-1, color="yellow", clear=True)

autostart = settings["autostart"]
wifi.radio.tx_power = float(settings["wifi_power"])

from web_interface import *
connect_to_network()

while 1:
    while not wifi.radio.connected and not wifi.radio.ap_active:
        check_network_again_timer = time.monotonic()
        start_hotspot()
    
    while wifi.radio.ap_active and not wifi.radio.connected: 
        ampule.listen(socket)
        if time.monotonic() > check_network_again_timer + 10:
            print("Attempting... " + str(wifi.radio.tx_power))
            wifi.radio.tx_power += 1
            if wifi.radio.tx_power == 20: wifi.radio.tx_power = 7
            if not first_start:
                check_network_again_timer = connect_to_network(timeout=3, silent=True)
            else: check_network_again_timer = time.monotonic()
        if first_start == False and wifi.radio.connected: wifi.radio.stop_ap()
        
    while wifi.radio.connected or wifi.radio.ap_active:
        settings["wifi_power"] = wifi.radio.tx_power
        pprint("Select app:")
        while wifi.radio.connected:# or wifi.radio.ap_active:
            first_start = False
            if autostart:
                print(ampule.listen(socket))
                load_settings.app_running = autostart
            elif not load_settings.app_running: ampule.listen(socket)
            if load_settings.app_running: 
                load_settings.app_running = initialize_app()
            
            b = check_if_button_pressed()
            if b == 0: pass
            if b == 1: next_program_in_list()
            elif b == 2: next_program_in_list(run=True)
            
            
