def fetch_data(host, port=80, args="", headers = "", filetype="text"):
    if varinit.if_long > 128 and not int(varinit.settings["listmode"]): version_delay(slowdown=1)
    
    data = ""
    cache = ""
    try: _from = binascii.hexlify(varinit.settings["stations"]["1"]["mystation"]).decode("utf-8")
    except: _from = binascii.hexlify(bytearray(varinit.settings["stations"]["1"]["mystation"])).decode("utf-8")
    headers = "User-Agent: " + str(id) + "\r\n"
    headers += "Accept: application/json\r\n" + "Content-Type: application/json\r\n" + "Host: " + host + "\r\n" + "Version: " + str(varinit.settings["version"]) + "\r\n"
    headers += "Uptime: " + str(round((time.monotonic() - varinit.starttime)/60)) + "\r\n"
    headers += "OS-Version: " + str(varinit.cpver) + "\r\n"
    headers += "Country: " + str(varinit.settings["stations"]["1"]["country"]) + "\r\n"
    headers += "Operator: " + str(varinit.settings["stations"]["1"]["operator"]) + "\r\n"
    headers += "Siteid: " + str(varinit.settings["stations"]["1"]["siteid"]) + "\r\n"
    headers += "From: " + str(_from) + "\r\n"
    headers += "User: " + str(varinit.settings["user"]) + "\r\n"
    headers += "Temperature: " + str(round(microcontroller.cpu.temperature))
    print("-Fetching------------------------------------------------ ")
    print("■ HOST: ", host)
    print("■ ARGS: ", args)
    print("■ PORT: ", port)
    print("■ FILETYPE: ", filetype)
    request = b"GET " + args + " HTTP/1.0\r\n" + headers + "\r\n\r\n"
    try:
        #with pool.socket(pool.AF_INET, pool.SOCK_STREAM) as s:
        with pool.socket() as s:
            cache = bytearray(100000)                                # MAX FILESIZE
            #s.setblocking(False)
            s.settimeout(varinit.socket_timeout)
            s.connect((host, port))
            sent = s.sendall(request)
            #buff = bytearray(512)
            buff = bytearray(8)
            data = s.recv_into(buff)
            while data:
                cache += buff[:data]
                data = s.recv_into(buff)
    except Exception as e: 
        print("Socket error: ", e)
        #if "-2" in str(e): reset()
        if "-2" in str(e): wifi.radio.enabled = False                  ######## TESTAR
            
    except: print("Socket error")
    try:
        if filetype == "binary":
            separator = b'\r\n\r\n'
            index = cache.find(separator)
            if index != -1: cache = cache[index+len(separator):]
            return cache
        x = cache.decode("utf-8")
        data = x.split("\r\n\r\n",1)[1]
    except: print("Reading error")
    
    try:
        date = x.split("Date:",1)[1]
        date = date.split("\r\n")[0]
        varinit.currenttime = convert_date(date)
    except: pass
    print("--------------------------------------------------------- ")
    if varinit.if_long > 128 and not int(varinit.settings["listmode"]): version_delay(slowdown=2)
    return data