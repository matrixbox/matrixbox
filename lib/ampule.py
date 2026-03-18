# Ändrad med headers från internet
import io
import re
import time
#from __main__ import buffer_size
from errno import EAGAIN, ECONNRESET

BUFFER_SIZE = 1024*4
_recv_buffer = bytearray(BUFFER_SIZE)
routes = []
variable_re = re.compile("^<([a-zA-Z]+)>$")

class Request:
    def __init__(self, method, full_path):
        self.method = method
        self.path = full_path.split("?")[0]
        self.params = Request.__parse_params(full_path)
        self.headers = {}
        self.body = None

    @staticmethod
    def __parse_params(path):
        query_string = path.split("?")[1] if "?" in path else ""
        param_list = query_string.split("&")
        params = {}
        for param in param_list:
            key_val = param.split("=")
            if len(key_val) == 2:
                params[key_val[0]] = key_val[1]
        return params


def __parse_headers(reader):
    headers = {}
    for line in reader:
        if line == b'\r\n': break
        title, content = str(line, "utf-8").split(":", 1)
        headers[title.strip().lower()] = content.strip()
    return headers

def __parse_body(reader):
    data = bytearray()
    for line in reader:
        if line == b'\r\n': break
        data.extend(line)
    return str(data, "utf-8")

def __read_request(client):
    message = bytearray()
    socket_recv = True
    
    for _ in range(10):
        try:
            while socket_recv:
                num_received = client.recv_into(_recv_buffer)
                chunk = _recv_buffer[:num_received]
                null_pos = -1
                for i in range(num_received):
                    if chunk[i] == 0x00:
                        null_pos = i
                        break
                if null_pos >= 0:
                    message.extend(chunk[:null_pos])
                    socket_recv = False
                else:
                    message.extend(chunk)
                break
        except OSError as error:
            time.sleep(0.01)
            continue

    reader = io.BytesIO(message)
    line = str(reader.readline(), "utf-8")
    parts = line.rstrip("\r\n").split(None, 2)
    if len(parts) < 3:
        return None
    (method, full_path, _) = parts

    request = Request(method, full_path)
    request.headers = __parse_headers(reader)
    request.body = __parse_body(reader)

    return request

def __send_response(client, code, headers, data):
    headers['Access-Control-Allow-Origin'] = '*'
    headers["Content-Type"] = "text/html"
    headers["Server"] = "Ampule/0.0.1-alpha (CircuitPython)"
    headers["Connection"] = "close"
    if isinstance(data, str):
        data = data.encode()
    headers["Content-Length"] = len(data)

    parts = []
    parts.append(("HTTP/1.0 %i OK\r\n" % code).encode())
    for k, v in headers.items():
        parts.append(("%s: %s\r\n" % (k, v)).encode())
    parts.append(b"\r\n")
    parts.append(data)
    parts.append(b"\r\n")
    response_buffer = b"".join(parts)

    # unreliable sockets on ESP32-S2: see https://github.com/adafruit/circuitpython/issues/4420#issuecomment-814695753
    response_length = len(response_buffer)
    bytes_sent_total = 0
    while True:
        try:
            bytes_sent = client.send(response_buffer)
            bytes_sent_total += bytes_sent
            if bytes_sent_total >= response_length:
                return bytes_sent_total
            else:
                response_buffer = response_buffer[bytes_sent:]
                continue
        except OSError as e:
            if e.errno == 11:       # EAGAIN: no bytes have been transfered
                time.sleep(0.1)
                continue
            else:
                return bytes_sent_total

def __on_request(method, rule, request_handler):
    regex = "^"
    rule_parts = rule.split("/")
    for part in rule_parts:
        # Is this portion of the path a variable?
        var = variable_re.match(part)
        if var:
            # If so, allow any alphanumeric value
            regex += r"([a-zA-Z0-9_-]+)\/"
        else:
            # Otherwise exact match
            regex += part + r"\/"
    regex += "?$"
    routes.append(
        (re.compile(regex), {"method": method, "func": request_handler})
    )

def __match_route(path, method):
    for matcher, route in routes:
        match = matcher.match(path)
        if match and method == route["method"]:
            return (match.groups(), route)
    return None

def listen(socket):
    try:
        client, _ = socket.accept()
    except OSError as e:
        if e.errno == EAGAIN: 
            #time.sleep(0.1)
            return
        if e.errno == ECONNRESET: return
        #print("OS Error with socket:", e)
        raise e

    try:
        request = __read_request(client)
        if request is None:
            client.close()
            return
        match = __match_route(request.path, request.method)
        if match:
            args, route = match
            status, headers, body = route["func"](request, *args)
            __send_response(client, status, headers, body)
        else:
            __send_response(client, 404, {}, "Not found")
    except BaseException as e:
        print("Error with request:", e)
        try:
            __send_response(client, 500, {}, "Error")
        except:
            pass
    client.close()

def route(rule, method='GET'):
    return lambda func: __on_request(method, rule, func)