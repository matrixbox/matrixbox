import load_screen, sys
from __main__ import *
#from lib.web_interface import url_decoder

exit = False
start_x = 300
padding_length = 30
with open("typewriter.html") as f: html = f.read()

@ampule.route("/exit", method="GET")
def webinterface(request):
    global exit
    exit = True
    return (200, {}, """<meta http-equiv="refresh" content="0; url=../" />""")

@ampule.route("/", method="POST")
def scroller_webinterface_port(request):
    global scroller_text, exit
    print("POSTED")
    if "text" in request.params: 
        print(url_decoder(request.params["text"]))
        pprint(url_decoder(request.params["text"]))
        refresh()
    

@ampule.route("/", method="GET")
def scroller_webinterface(request):
    print(request.params)
    return (200, {}, html)


clearscreen()

while not exit:
    ampule.listen(socket)
    b = check_if_button_pressed()
    if b == 2: sys.exit()
        
 

clearscreen()