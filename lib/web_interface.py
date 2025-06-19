from fetch_data import fetch
from load_settings import savesettings
from __main__ import *
import __main__
#from main import connect_to_network
#import __main__
#print(dir(__main__))
exitbutton = """<html><a href="/exit">&#x274C;</a>"""
backbutton = """<br><button onclick="location.href='../'">&larr; Back</button>"""
bootloaderbutton = """<button class="center" onclick="window.location.href='/bootloader'" style='background-color:red'> Bootloader </button>"""
#unlock = """<button class="center" onclick="window.location.href='/unlock'" style='background-color:yellow'> &#128275; </button>"""
unlock = """<button class="center" style='background-color:yellow' onclick="fetch('/?unlock=true', {method: 'POST'})">🔓</button>"""

def textbox(settings):
    settings_html = """<form action="/" method="POST">"""
    for setting in settings:
      print("Setting: ", setting)
      settings_html += f"""<label for="{setting}">{setting}</label>
    <input type="text" id="{setting}" name="{setting}" placeholder="{str(settings[setting])}"><br>"""
    return settings_html + """<br><button type="submit" value="Submit">Save</button></form>"""
    
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
    error_color = "green"
    microcontroller.cpu.frequency = 240000000
    for x, file in enumerate(applist[app]):
        clearscreen()
        if "/" in file:
            directory_name = "/".join(file.split("/")[:-1])
            print(directory_name)
            try: os.mkdir(directory_name)
            except: pass
            
        print("File: ", file)
        print(app + "/" + file)
        file_url = settings["repository_url"] + app + "/"
        print(file_url)
        pprint(str(x+1) + "/" + str(no_of_files) + " Downloading: ")#, line=0,  _clearscreen=True)
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
        except: 
            pprint("Read only!", color="red")
            error_color = "red"
    microcontroller.cpu.frequency = 180000000 ### notering
    
    pprint("Done.", color=error_color, line=-1, _refresh=True)
    os.chdir("/")
        


def get_updates():
    print(settings)
    try:
        updates = json.loads(requests.get((settings["repository_url"]+settings["repository_file"])).text)
    except Exception as e:
        print(e)
    return updates
    
def list_available_apps(apps):
    print("Apps: ", apps)
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
            </script>

            <script>
            document.addEventListener("DOMContentLoaded", function() {
    const ssidDropdown = document.getElementById("ssid");
    updateVariable({ target: ssidDropdown }); // Trigger update for single SSID
});</script>


            """ + """

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
  <h1>MatrixBox</h1>
 
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

@ampule.route('/', method="POST")
def webinterface_post(request):
    global settings
    print("POSTED!")
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
            if parsed_data[setting]:
                try: settings[setting] = parsed_data[setting]
                except: pass
        savesettings(settings)
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
        if "password" in request.params:
            __main__.settings["password"] = url_decoder(request.params["password"])
            #wifi.radio.connect(settings["ssid"], settings["password"])
        if "delete" in request.params:
            dir = request.params["delete"]
            os.chdir(dir)
            
            for file in os.listdir():
                clearscreen()
                try: 
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
    return (200, {}, """<meta http-equiv="refresh" content="0; url=../" />""")

@ampule.route('/bootloader')
def bootloader(request):
    import microcontroller
    microcontroller.on_next_reset(microcontroller.RunMode.BOOTLOADER)
    microcontroller.reset()
    return (200, {}, "None")

@ampule.route("/settings")
def _settings(request):
    global settings
    settings_html = header("Settings")+f"""
    <div class="header">
  <h1>SETTINGS</h1>
  <p>Edit your settings and save:</p>
  {textbox(settings)}
  
</div>
    """ + bootloaderbutton + unlock + footer(True)
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
"%C5%A1":"\u0161"}

    for char in url_decode: url = url.replace(char, url_decode[char])
    return url

