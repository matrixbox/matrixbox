from __main__ import *
import time, json, os, gc, load_settings
from load_screen import *
from check_button import check_if_button_pressed

SYSTEM_PROMPT = """You generate CircuitPython apps for MatrixBox, an ESP32-S3 with an RGB LED matrix display.
Output ONLY the Python code for code.py. No markdown fences, no explanations before or after.

Available via `from __main__ import *`:
- window: displayio.Bitmap(width, height, 10) for pixel drawing
- settings: dict with keys "width", "height", "rotation", etc.
- pprint(string, line=False, color="white"): draw text on LED matrix
  Colors: "white","yellow","red","blue","green","orange","pink","grey","brightwhite"
- pset(x, y, color_index): draw single pixel
  Palette: 0=background, 1=yellow, 2=bright_white, 3=blue, 4=red, 5=white, 7=green, 8=pink, 11=orange
- refresh(): push framebuffer to display
- clearscreen(on_or_off=False, lines=False): clear display
- ampule: tiny web framework, @ampule.route("/path", method="GET") decorator
- socket: pass to ampule.listen(socket) in main loop to handle web requests
- load_settings: set load_settings.app_running = False to exit the app
- requests: adafruit_requests.Session with SSL (supports .get()/.post())
- wifi, time, os, json, math, random, microcontroller, board, digitalio

Button input: `from check_button import check_if_button_pressed`
b = check_if_button_pressed() returns 0 (none), 1 (short press), 2 (long press)

Required code.py structure:

from __main__ import *
import time, load_settings
from load_screen import *
from check_button import check_if_button_pressed

@ampule.route("/", method="GET")
def app_ui(request):
    return (200, {}, "<html>Your UI<br><a href='/exit'>Exit</a></html>")

@ampule.route("/exit", method="GET")
def exit_route(request):
    load_settings.app_running = False
    return (200, {}, '<meta http-equiv="refresh" content="0; url=../" />')

width = settings["width"]
height = settings["height"]

while load_settings.app_running:
    # Drawing / app logic here
    refresh()
    ampule.listen(socket)
    b = check_if_button_pressed()
    if b == 2: load_settings.app_running = False

Rules:
- MUST use `while load_settings.app_running:` as main loop condition
- MUST include an /exit route that sets load_settings.app_running = False
- MUST call refresh() after drawing and ampule.listen(socket) each iteration
- Keep code simple and memory-efficient (microcontroller with limited RAM)
- Do not use asyncio or threading"""

INIT_CODE = "from __main__ import *\nampule.routes.clear()\n\nimport code\n"


def _generate(app_name, prompt, key, provider="anthropic", model="claude-sonnet-4-20250514"):
    clearscreen(lines=True)
    pprint("Generating...")
    pprint(app_name)

    gc.collect()

    if provider == "anthropic":
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        body = {
            "model": model,
            "max_tokens": 4096,
            "system": SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": prompt}],
        }
    elif provider == "gemini":
        url = "https://generativelanguage.googleapis.com/v1beta/models/" + model + ":generateContent?key=" + key
        headers = {"content-type": "application/json"}
        body = {
            "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"maxOutputTokens": 4096},
        }
    else:  # openai, openrouter, github
        if provider == "openrouter":
            url = "https://openrouter.ai/api/v1/chat/completions"
        elif provider == "github":
            url = "https://models.github.ai/inference/chat/completions"
        else:
            url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": "Bearer " + key,
            "content-type": "application/json",
        }
        body = {
            "model": model,
            "max_tokens": 4096,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        }

    try:
        resp = requests.post(url, json=body, headers=headers)
        status = resp.status_code
        data = resp.json()
        resp.close()
        gc.collect()
    except Exception as e:
        pprint("API Error!", color="red")
        print("API call error:", e)
        return {"error": str(e)}

    if status != 200:
        err = data.get("error", {})
        if isinstance(err, dict):
            err = err.get("message", "HTTP " + str(status))
        pprint("Error!", color="red")
        print("API error:", err)
        return {"error": str(err)}

    try:
        if provider == "anthropic":
            code_text = data["content"][0]["text"]
        elif provider == "gemini":
            code_text = data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            code_text = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        return {"error": "Unexpected API response format"}

    del data
    gc.collect()

    # Strip markdown fences if Claude included them
    if "```python" in code_text:
        code_text = code_text.split("```python", 1)[1].rsplit("```", 1)[0]
    elif "```" in code_text:
        code_text = code_text.split("```", 1)[1].rsplit("```", 1)[0]
    code_text = code_text.strip()

    # Save the new app
    os.chdir("/")
    try:
        os.mkdir(app_name)
    except OSError:
        pass

    try:
        clearscreen(True)
        with open(app_name + "/__init__.py", "w") as f:
            f.write(INIT_CODE)
        with open(app_name + "/code.py", "w") as f:
            f.write(code_text)
        clearscreen(False)
    except Exception as e:
        clearscreen(False)
        pprint("Write error!", color="red")
        print("File write error:", e)
        return {"error": "Save failed: " + str(e)}

    # Persist API key for reuse
    key_name = "claude_key" if provider == "anthropic" else provider + "_key"
    settings[key_name] = key
    try:
        from __main__ import savesettings
        savesettings(settings)
    except Exception as e:
        print("Could not save key:", e)

    pprint("Done!", color="green")
    pprint(app_name, color="green")
    gc.collect()
    return {"success": True, "app_name": app_name}


def _build_page():
    ip = str(wifi.radio.ipv4_address) if wifi.radio.ipv4_address else "OFFLINE"

    keys_js = json.dumps({
        "anthropic": settings.get("claude_key", ""),
        "openai": settings.get("openai_key", ""),
        "gemini": settings.get("gemini_key", ""),
        "openrouter": settings.get("openrouter_key", ""),
        "github": settings.get("github_key", ""),
    })

    apps = []
    for d in os.listdir("/"):
        try:
            if "__init__.py" in os.listdir("/" + d):
                apps.append(d)
        except:
            pass

    app_chips = "".join(
        '<span class="app-chip">' + a + "</span>" for a in apps
    )
    apps_js = json.dumps(apps)

    return (
        '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1.0">'
        "<title>AppMaker</title><style>"
        + css()
        + ".app-chip{display:inline-block;background:var(--surface2);border:1px solid var(--border);"
        "border-radius:8px;padding:5px 12px;font-size:.82rem;color:var(--accent2);"
        "font-weight:500;text-transform:capitalize}"
        "textarea{width:100%;background:var(--surface2);border:1.5px solid var(--border);"
        "border-radius:var(--r);padding:10px 13px;color:var(--text);font-size:.95rem;"
        "font-family:inherit;outline:none;resize:vertical}"
        "textarea:focus{border-color:var(--accent)}"
        ".provider-tag{font-size:.7rem;color:var(--muted);margin-left:6px}"
        "</style></head><body>"
        '<nav class="navbar">'
        '<a class="nav-brand">MatrixBox</a>'
        '<span class="nav-link" style="color:var(--text)">AppMaker</span>'
        '<div class="nav-spacer"></div>'
        '<div class="nav-info"><span>' + ip + "</span></div>"
        '<a class="nav-x" href="/exit" title="Exit">&#x2715;</a>'
        "</nav>"
        '<div class="page">'
        '<div class="logo"><h1>&#x2728; AppMaker</h1>'
        "<p>Generate apps with AI</p></div>"
        # ── API settings card ──
        '<div class="card">'
        '<div class="section-title">API Settings</div>'
        "<label>Provider</label>"
        '<select id="provider" onchange="sp()">'
        '<option value="anthropic">Anthropic (Claude)</option>'
        '<option value="openai">OpenAI (ChatGPT)</option>'
        '<option value="gemini">Google Gemini</option>'
        '<option value="openrouter">OpenRouter</option>'
        '<option value="github">GitHub Copilot</option>'
        "</select>"
        '<label id="key_label">API Key</label>'
        '<input type="password" id="api_key" placeholder="sk-ant-...">'
        "<label>Model</label>"
        '<select id="model"></select></div>'
        # ── New app card ──
        '<div class="card">'
        '<div class="section-title">New App</div>'
        '<label for="app_name">App Name</label>'
        '<input type="text" id="app_name" placeholder="my_cool_app">'
        '<label for="prompt">Describe Your App</label>'
        '<textarea id="prompt" rows="6" placeholder="A colorful clock that draws the time with pixels, '
        'cycling through rainbow colors every second..."></textarea>'
        '<button class="btn btn-full" id="gen_btn" onclick="generate()">&#x2728; Generate App</button>'
        '<div id="status" style="margin-top:12px;font-size:.85rem;color:var(--muted);text-align:center"></div>'
        "</div>"
        # ── Installed apps card ──
        '<div class="card">'
        '<div class="section-title">Installed Apps</div>'
        '<div style="display:flex;flex-wrap:wrap;gap:6px">'
        + app_chips
        + "</div></div>"
        "</div>"  # close .page
        "<script>"
        "var existingApps=" + apps_js + ";"
        "var savedKeys=" + keys_js + ";"
        "var providers={"
        "anthropic:{ph:'sk-ant-...',models:[['claude-sonnet-4-20250514','Claude Sonnet 4'],['claude-haiku-4-20250414','Claude Haiku 4']]},"
        "openai:{ph:'sk-...',models:[['gpt-4o-mini','GPT-4o Mini'],['gpt-4o','GPT-4o']]},"
        "gemini:{ph:'AIza...',models:[['gemini-2.0-flash','Gemini 2.0 Flash'],['gemini-2.5-flash','Gemini 2.5 Flash']]},"
        "openrouter:{ph:'sk-or-...',models:[['google/gemini-2.0-flash-exp:free','Gemini Flash (Free)'],['meta-llama/llama-4-scout-17b-16e-instruct:free','Llama 4 Scout (Free)'],['anthropic/claude-sonnet-4','Claude Sonnet 4']]},"
        "github:{ph:'github_pat_...',models:[['openai/gpt-4o-mini','GPT-4o Mini'],['openai/gpt-4o','GPT-4o'],['meta/llama-4-scout-17b-16e-instruct','Llama 4 Scout']]}"
        "};"
        "function sp(){"
        "var pv=document.getElementById('provider').value;"
        "var info=providers[pv];"
        "var ki=document.getElementById('api_key');"
        "ki.placeholder=info.ph;"
        "ki.value=savedKeys[pv]||'';"
        "var sel=document.getElementById('model');"
        "sel.innerHTML='';"
        "info.models.forEach(function(m){var o=document.createElement('option');o.value=m[0];o.textContent=m[1];sel.appendChild(o)});"
        "}"
        "sp();"
        "async function generate(){"
        "var btn=document.getElementById('gen_btn');"
        "var st=document.getElementById('status');"
        "var provider=document.getElementById('provider').value;"
        "var key=document.getElementById('api_key').value.trim();"
        "var raw=document.getElementById('app_name').value.trim().toLowerCase();"
        "var name=raw.replace(/[^a-z0-9_]/g,'_').replace(/^_+|_+$/g,'');"
        "var prompt=document.getElementById('prompt').value.trim();"
        "var model=document.getElementById('model').value;"
        "if(!key){st.innerHTML='<span style=\"color:#ff7070\">Enter your API key</span>';return;}"
        "if(!name){st.innerHTML='<span style=\"color:#ff7070\">Enter an app name</span>';return;}"
        "if(!prompt){st.innerHTML='<span style=\"color:#ff7070\">Describe what the app should do</span>';return;}"
        "if(existingApps.indexOf(name)!==-1&&!confirm('App \"'+name+'\" exists. Overwrite?'))return;"
        "btn.disabled=true;btn.innerHTML='&#x23F3; Generating...';"
        "st.innerHTML='Generating&hellip; this may take 30+ seconds';"
        "try{"
        "var r=await fetch('/generate',{method:'POST',"
        "headers:{'X-Api-Key':key,'X-App-Name':name,'X-Model':model,'X-Provider':provider},"
        "body:prompt});"
        "var d=await r.json();"
        "if(d.success){"
        "savedKeys[provider]=key;"
        "st.innerHTML='<span style=\"color:#00e676\">&#x2714; App \"'+d.app_name+'\" created!</span>"
        "<br><a href=\"/exit\" class=\"btn btn-sm\" style=\"margin-top:8px\">&#x2190; Back to menu</a>';"
        "}else{"
        "st.innerHTML='<span style=\"color:#ff7070\">&#x2718; '+(d.error||'Unknown error')+'</span>';"
        "}"
        "}catch(e){"
        "st.innerHTML='<span style=\"color:#ff7070\">Connection error: '+e.message+'</span>';"
        "}"
        "btn.disabled=false;btn.innerHTML='&#x2728; Generate App';"
        "}"
        "</script></body></html>"
    )


@ampule.route("/", method="GET")
def app_creator_home(request):
    return (200, {}, _build_page())


@ampule.route("/generate", method="POST")
def handle_generate(request):
    try:
        key = request.headers.get("x-api-key", "")
        name = request.headers.get("x-app-name", "")
        model = request.headers.get("x-model", "claude-sonnet-4-20250514")
        provider = request.headers.get("x-provider", "anthropic")
        prompt = request.body.strip() if request.body else ""

        # Sanitize app name
        clean = ""
        for c in name.lower():
            if c.isalpha() or c.isdigit() or c == "_":
                clean += c
        name = clean.strip("_")

        if not key or not name or not prompt:
            return (200, {}, json.dumps({"error": "Missing required fields"}))

        result = _generate(name, prompt, key, provider, model)
        return (200, {}, json.dumps(result))
    except Exception as e:
        print("Generate error:", e)
        return (200, {}, json.dumps({"error": str(e)}))


@ampule.route("/exit", method="GET")
def exit_creator(request):
    load_settings.app_running = False
    return (200, {}, '<meta http-equiv="refresh" content="0; url=../" />')


# ── Show status on LED matrix ──
clearscreen(lines=True)
pprint("AppMaker")
_addr = str(wifi.radio.ipv4_address) if wifi.radio.ipv4_address else "OFFLINE"
pprint(_addr)
pprint("Open browser")

# ── Main loop ──
while load_settings.app_running:
    ampule.listen(socket)
    b = check_if_button_pressed()
    if b == 2:
        load_settings.app_running = False
