from fetch_data import fetch
from __main__ import *
import __main__
#from main import connect_to_network
#import __main__
#print(dir(__main__))
exitbutton = """<html><a href="/exit">&#x274C;</a>"""
backbutton = """<br><button onclick="location.href='../'">&larr; Back</button>"""
bootloaderbutton = """<button class="center" onclick="window.location.href='/bootloader'" style='background-color:red'> Bootloader </button>"""

def install_app(app):
    if app == "system": app = "/"
    print("Install: ", app)
    applist = load_settings.latest_available_apps
    no_of_files = len(applist[app])
    print("Applist: ", applist, " Files: ", no_of_files)
    os.chdir("/")
    try: os.mkdir(app)
    except: pass
    try: os.chdir(app)
    except: pass
    
    for x, file in enumerate(applist[app]):
        if "/" in file:
            directory_name = "/".join(file.split("/")[:-1])
            print(directory_name)
            try: os.mkdir(directory_name)
            except: pass
            
        print("File: ", file)
        print(app + "/" + file)
        file_url = settings["repository"]["url"] + app + "/"
        print(file_url)
        pprint(str(x+1) + "/" + str(no_of_files) + " Downloading: ", line=0,  _clearscreen=True)
        pprint(str(file) + "...")
        downloaded_file = requests.get(file_url + file)
        pprint(str(downloaded_file.status_code))
        if ".mpy" in file: 
            downloaded_file = bytearray(downloaded_file.content)
            writemode = "wb"
        else: 
            downloaded_file = downloaded_file.text
            writemode = "w"
        clearscreen()
        try: 
            with open(str(file), writemode) as f: f.write(downloaded_file)
        except: pprint("Read only!", _clearscreen=True)

    os.chdir("/")
        


def get_updates():
    return json.loads(requests.get((settings["repository"]["url"]+settings["repository"]["file"])).text)
    
def list_available_apps(apps):
    load_settings.latest_available_apps = apps
    applist = """<br><br>
    """ + f"""System: <button id='system' onclick="install"""+"system"+"""()">Update</button>

                   """ + """
                   <script>function install"""+"system"+"""() {
    fetch("/?install="""+"system"+"""", { method: "POST" }).then(() => {
        setTimeout(() => {
            window.location.href = "/download"; // Redirect after 2 seconds
        }, 10); // 2000 milliseconds = 2 seconds
    });
}
</script><br>"""


    for dir in apps:
        if dir == "/" or dir == "lib": continue
        if dir in os.listdir() and "__init__.py" in os.listdir(dir):
            applist += f"""{dir}: <button id='{dir}' onclick="delete"""+dir+"""()">Delete</button>

                   """ + """
                   <script>function delete"""+dir+"""() {
    fetch("/?delete="""+dir+"""", { method: "POST" }).then(() => {
        setTimeout(() => {
            window.location.href = "/download"; // Redirect after 2 seconds
        }, 10); // 2000 milliseconds = 2 seconds
    });
}
</script>"""
        else: applist += f"""{dir}: <button id='{dir}' onclick="install"""+dir+"""()">Install</button>

                   """ + """
                   <script>function install"""+dir+"""() {
    fetch("/?install="""+dir+"""", { method: "POST" }).then(() => {
        setTimeout(() => {
            window.location.href = "/download"; // Redirect after 2 seconds
        }, 10); // 2000 milliseconds = 2 seconds
    });
}
</script>"""
        applist += "<br>"
        #for file in apps[dir]:
        #    print(dir + "/" + file)
    return applist


def latest_wifi_error():
    return str(__main__.wifi_status)

def css():
    return """
@charset "UTF-8";
body {
            margin: 0;
            background-color: black;

            justify-content: center;
            align-items: center;
            height: 100vh;
            color: white;
            font-family: Arial, sans-serif;
            }
button {
         
         margin: 0 auto;
        }
.header {
  padding: 10px;
  text-align: center;
  background: #black;
  color: white;
  font-size: 30px;
}

.content {padding:20px;}
        .dropdown-container {
            display: flex;
            align-items: center;
        }
        select {
            border-radius: 10px;
            padding: 8px;
            border: none;
            outline: none;
            font-size: 16px;
        }
        button {
            margin-left: 10px;
            padding: 8px 16px;
            border: none;
            background-color: #0081e3;
            color: white;
            font-size: 16px;
            border-radius: 10px;
            cursor: pointer;
        }
        button:hover {
            background-color: #028ef7;
        }

.center {
  margin-left: auto;
  margin-right: auto;
}
"""

def header(title="Settings"):
    return f"""<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
<style> {css()} </style>
<body><table class="center"><tr><td>"""

def footer(back=False):
    back = backbutton if back else ""
    return f"""{back}</td></tr></table></body></html>"""

def connect_to_wifi():
#def select_app():
    def scan():
        networks = ""
        for network in wifi.radio.start_scanning_networks(start_channel=1, stop_channel=14):
            networks += f"<option value='{network.ssid}'>{network.ssid}</option>"
            print(network.ssid)
        wifi.radio.stop_scanning_networks()
        return networks
    networks = scan()
    
    return header("Connect to WIFI") + f"""
  
  <h1>Select network:</h1>
  <br>
  
          <div class="dropdown-container">
            <select id="ssid" name="ssid">
            {networks}
            </select> 
            
            """ + """<script>
            function updateVariable(event) {
            const selectedValue = event.target.value;
            const encodedSSID = selectedValue.replace(/#/g, '%23');
            fetch(`/?ssid=${encodedSSID}`, {
                method: 'POST',
                })
                }
                document.getElementById("ssid").addEventListener("change", updateVariable);
            </script>""" + """

            <input type="text" id="password" class="form-control" name="password" placeholder="*******" value="">
                """ + """
                <script>
                function updateVariable(event) {
                    const password = event.target.value;
                    const encodedPassword = password.replace(/#/g, '%23');
                    fetch(`/?password=${encodeURIComponent(encodedPassword)}`, {
                        method: 'POST',
                    })
                }
                document.getElementById("password").addEventListener("blur", updateVariable);
                </script> """ + """


            
            <button onclick="location.href='/connect'">Connect</button>
        </div>
    <br>
    """ + latest_wifi_error() + footer()

def select_app():
    installed_apps = ""
    for app in os.listdir():
        if not "." in app: #installed_apps.append(app)
            if not "__init__.py" in os.listdir(app): continue
            installed_apps += f"""
                <tr>
                <td>{app}</td>
                <td>
                   <button id='{app}' onclick="run"""+app+"""()">Run</button>

                   """ + """
                   <script>function run"""+app+"""() {
    fetch("/?run="""+app+"""", { method: "GET" }).then(() => {
        setTimeout(() => {
            window.location.href = "/"; // Redirect after 2 seconds
        }, 10); // 2000 milliseconds = 2 seconds
    });
}
</script>""" + """
                </td>
            </tr>
            """
    return header("Select app") + f"""
    <div class="header">
  <h1>EuroSign</h1>
  <p>Choose app:</p>
</div>
    <table class="center">{installed_apps}</table>
    <br>
    <button class="center" onclick="window.location.href='/download'"> Download </button>
    <br>
    <hr>
    <button class="center" onclick="window.location.href='/settings'"> Settings </button>
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

@ampule.route("/", method="POST")
def webinterface_post(request):
    print("POSTED:", request.params)
    
    try: 
        if "ssid" in request.params:
            __main__.settings["ssid"] = request.params["ssid"]
        if "password" in request.params:
            __main__.settings["password"] = request.params["password"]
            #wifi.radio.connect(settings["ssid"], settings["password"])
        if "delete" in request.params:
            dir = request.params["delete"]
            os.chdir(dir)
            try:
                for file in os.listdir():
                    clearscreen()
                    os.remove(file)
                    pprint("Removed: ", file)
            except Exception as e: 
                pprint(str(e))
            os.chdir("/")
            os.rmdir(dir)
        if "install" in request.params:
            print(request.params["install"])
            install_app(request.params["install"])
    except Exception as e: print(e)
    return (200, {}, "None")

@ampule.route('/bootloader')
def bootloader(request):
    import microcontroller
    microcontroller.on_next_reset(microcontroller.RunMode.BOOTLOADER)
    microcontroller.reset()
    return (200, {}, "None")

@ampule.route('/settings')
def _settings(request):
    global settings
    #settings = load_settings.settings()
    _settings = ""
    for setting in settings:
        _settings += f"{str(setting)} : {settings[setting]}<br>"
    print(_settings)
    settings_html = header("Settings")+f"""
    <div class="header">
  <h1>SETTINGS</h1>
  <p>Edit your settings and save:</p>
  {_settings}
  <button onclick="location.href='/save'">Save</button>
</div>
    """ + bootloaderbutton + footer(True)
    return (200, {}, settings_html)

@ampule.route("/save")
def _save(request):
    global settings
    try: load_settings.savesettings(settings)
    except: print("Failed to save!")
    save_html = header() + f"""test""" + footer()
    return (200, {}, save_html)

@ampule.route('/download')
def download(request):
    content = f"""
    Download:
    """ + str(list_available_apps(get_updates()))
    return (200, {}, header("Download apps") + content + backbutton + footer())


####################################################
# DEBUG FUNKTIONER
####################################################

@ampule.route('/cmd', method='POST')
def execute_command(request):
    command = request.headers["x-command"]
    _c = str(command)
    _e = ""
    try:
        exec(command)
    except Exception as e:
        _e = str(e)
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Console and Command</title>
    <style>
        ...
    </style>
</head>
<body>
""" + e + """<br>""" + _c + """
    <div id="console-output"></div>
    <input id="command-input" type="text" placeholder="Enter command...">
    <button id="command-button">Execute</button>
<script>
    let outputConsole = document.getElementById('console-output');
    let commandInput = document.getElementById('command-input');
    let commandButton = document.getElementById('command-button');

    console.log('JavaScript is running...');

    commandButton.addEventListener('click', async () => {
        console.log('Button clicked...');
        let command = commandInput.value;
        console.log('Command:', command);

        if (command) {
            console.log('Sending command to server...');
            const endpoint = 'cmd';

            try {
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Command': command,
                    },
                    body: null,
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }

                const data = await response.json();
                console.log('Response from server:', data);

                outputConsole.innerHTML += `${command}\n`;
            } catch (error) {
                console.error('Error sending command:', error);
            }
        }
    });
</script>
</body>
</html>"""    
    
    return (200, {}, html)


@ampule.route("/cmd", method="GET")
def _cmd(request):
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Console and Command</title>
    <style>
        ...
    </style>
</head>
<body>
    <div id="console-output"></div>
    <input id="command-input" type="text" placeholder="Enter command...">
    <button id="command-button">Execute</button>
<script>
    let outputConsole = document.getElementById('console-output');
    let commandInput = document.getElementById('command-input');
    let commandButton = document.getElementById('command-button');

    console.log('JavaScript is running...');

    commandButton.addEventListener('click', async () => {
        console.log('Button clicked...');
        let command = commandInput.value;
        console.log('Command:', command);

        if (command) {
            console.log('Sending command to server...');
            const endpoint = 'cmd';

            try {
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Command': command,
                    },
                    body: null,
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }

                const data = await response.json();
                console.log('Response from server:', data);

                outputConsole.innerHTML += `${command}\n`;
            } catch (error) {
                console.error('Error sending command:', error);
            }
        }
    });
</script>
</body>
</html>"""
    return (200, {}, html)


@ampule.route("/settingsx")
def showsettings(request):
    return (200, {}, str(settings))

@ampule.route('/reset')
def reset(request): microcontroller.reset()

