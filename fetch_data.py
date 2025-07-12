from __main__ import *

def fetch(host, args="", port=80, headers = "", filetype="text", get_time=False):
    if ".mpy" in args: filetype = "binary"
    headers = "User-Agent: " + str(macid) + "\r\n" + "Accept: application/json\r\n" + "Content-Type: application/json\r\n" + "Host: " + host + "\r\n"
    print(f"""-Fetching------------------------------------------------ 
    ■ HOST: {host}
    ■ ARGS: {args}
    ■ PORT: {port}
    ■ FILETYPE: {filetype}""")
    try:
        with pool.socket() as s:
            cache = bytearray(100000)                                # MAX FILESIZE
            s.settimeout(5)
            s.connect((host, port))
            s.sendall(b"GET " + args + " HTTP/1.0\r\n" + headers + "\r\n\r\n")
            buff = bytearray(8)
            data = s.recv_into(buff)
            while data:
                cache += buff[:data]
                data = s.recv_into(buff)
    except Exception as e: print("Error: ", e)
    try:
        separator = b'\r\n\r\n'
        index = cache.find(separator)
        headers = {}
        if filetype == "binary":
            if index != -1:
                raw_headers = cache[:index]
                body = cache[index + len(separator):]
                decoded_headers = raw_headers.decode("utf-8")
                for line in decoded_headers.splitlines():
                    if ": " in line:
                        key, value = line.split(": ", 1)
                        headers[key] = value
                print("Headers:", headers)
                print("Size according to headers:", headers["Content-Length"])
                print("Size of binary body:", len(body))
                if not int(headers["Content-Length"]) == len(body): return 0
                return body
            else: return 0
        else:
            x = cache.decode("utf-8")
            
            if get_time: 
                date = x.split("Date:",1)[1]
                date = date.split("\r\n")[0]
                return date[18:26]
            
            _headers, data = x.split("\r\n\r\n", 1)
            for line in _headers.splitlines():
                if ": " in line:
                    key, value = line.split(": ", 1)
                    headers[key] = value
            print(f"Size according to headers: {headers['Content-Length']}")
            print(f"Size according to len: {len(data.encode('utf-8'))}")
            if not int(headers["Content-Length"]) == len(data.encode("utf-8")):
                return 0
            return data
    except Exception as e: print(e)
    print("--------------------------------------------------------- ")
    return data