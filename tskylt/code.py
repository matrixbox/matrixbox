import os
if "__init__.py" in os.listdir(): 
    print("__init__ found")
    from __main__ import *
else:
    import wifi, socketpool, time                                           # -- == T-Skylt == -- 
    wifi.radio.tx_power = 14.0                                              #       av Alex
    pool = socketpool.SocketPool(wifi.radio)                                #       och Parham
    socket = pool.socket()
stop_wifi = True
from functions import *
if "__init__.py" in os.listdir(): 
    from check_button import *
    varinit.last_button_state = last_button_state
    varinit.button = button
    varinit.gbutton = gbutton
    varinit.debounce_delay = debounce_delay
if varinit.cpver == 9: delay = version_delay()
else: pass#start_ap()
if not "__init__.py" in os.listdir(): 
    socket.setblocking(False)                                               # HTTP ###############################
    try: socket.setsockopt(pool.SOL_SOCKET, pool.SO_REUSEADDR, 1)
    except: print("Can not set SO_REUSEADDR...")
    socket.bind(('', 80))
    socket.listen(5)
else:
    from functions import refresh
disp_init()
scroll_mode()
def check_button():
    if varinit.last_button_state:
        if not varinit.button.value:
            varinit.time.sleep(varinit.debounce_delay)
            if not varinit.button.value:
                varinit.shared["nightcount"] = 0
                x = 0 
                while not varinit.button.value and x < varinit.button_delay * 2: x+=1
                if x > varinit.button_delay and not varinit.group.hidden:# and not varinit.if_long > 128:
                    varinit.deviations_timer = time.monotonic()
                    varinit.settings["listmode"] = 1 - int(varinit.settings["listmode"])
                    switch(_screen = True)
                else:
                    nightcheck(_switch=True, turnon=varinit.group.hidden); refresh()
    varinit.last_button_state = varinit.button.value

while 1:
    while wifi.radio.connected == False:                                # CHECK CONNECTION ###################
        wifi.radio.enabled = True ####### TEST
        wifi.radio.start_dhcp()
        start_ap()
        stop_wifi = False
        if varinit.tg3.y == 32: functions.switch(force=True, wifi_screen=True)
        varinit.reset_timer = time.monotonic()
        while wifi.radio.connected == False:
            if time.monotonic() > varinit.reset_timer + varinit.network_delay:
                wd()
                varinit.reset_timer = time.monotonic()                  
                wifiattempt(errmsg=False, _timeout=1, skipversion=True)
                update_screen()
            ampule.listen(socket)
        #if varinit.first_start: topbottom.fill(0);renderstring("^ " + str(wifi.radio.ipv4_address), block=True, _refresh=True)
            
    if varinit.settings["listmode"] and not varinit.tg3.y == 0: functions.switch(force=False, _cls=bottom)
    varinit.first_start = False
    if stop_wifi: wifi.radio.stop_ap()
    #check_version()
    x = 1
    while wifi.radio.connected == True:                                 # MAINLOOP ###########################
        x = 1 - x
        if x: 
            ampule.listen(socket)
            wd()
            check_button()
            
        
        if int(varinit.settings["listmode"]) and time.monotonic() > varinit.shared["scroll_timer"] + updatedelay: varinit.shared["scroll_timer"] = list_mode()
        elif not int(varinit.settings["listmode"]): 
            varinit.tg2.x -= 1
            refresh(int(delay + varinit.settings["scroll"]) + 1 * (delay*2))
            if varinit.tg2.x < -varinit.scrollsum: scroll_mode()
            elif time.monotonic() > varinit.shared["scroll_timer"] + updatedelay and shared["loop_counter"] >= 0: scroll_mode()
        