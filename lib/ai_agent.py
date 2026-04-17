import json, os, gc, time
from binascii import a2b_base64

_PROMPT_PATH = "/system_prompt.md"
_FALLBACK = "You are a helpful assistant for MatrixBox (ESP32-S3, CircuitPython 9). Respond with JSON: {\"reply\":\"...\", \"tools\":[...]}"

def _load_prompt():
    try:
        with open(_PROMPT_PATH) as f:
            return f.read()
    except:
        return _FALLBACK

def _refresh_prompt():
    """Fetch latest system_prompt.md from repo and cache locally."""
    try:
        import load_settings
        url = load_settings.settings().get("repository_url", "")
        if not url:
            return "no repository_url"
        url = url.rstrip("/") + "/system_prompt.md"
        session = _get_session()
        gc.collect()
        resp = session.get(url)
        if resp.status_code == 200:
            txt = resp.text
            resp.close()
            with open(_PROMPT_PATH, "w") as f:
                f.write(txt)
            del txt
            gc.collect()
            return "ok"
        else:
            resp.close()
            return "http " + str(resp.status_code)
    except Exception as e:
        return str(e)

LOG_PATH = "/ai_log.json"
MAX_HISTORY = 20

def _push_prompt():
    """Push local system_prompt.md to GitHub repo (requires contents:write PAT)."""
    try:
        import load_settings
        s = load_settings.settings()
        repo_url = s.get("repository_url", "")
        ai_key = s.get("ai_key", "")
        if not repo_url or not ai_key:
            return "no repository_url or ai_key"
        # Extract owner/repo from raw URL
        # e.g. https://raw.githubusercontent.com/matrixbox/matrixbox/refs/heads/main/
        parts = repo_url.replace("https://raw.githubusercontent.com/", "").strip("/").split("/")
        if len(parts) < 2:
            return "bad repo url"
        owner, repo = parts[0], parts[1]
        with open(_PROMPT_PATH) as f:
            content = f.read()
        from binascii import b2a_base64
        b64 = b2a_base64(content.encode("utf-8")).decode("ascii").replace("\n", "")
        # Get current file SHA (required for update)
        api_url = "https://api.github.com/repos/" + owner + "/" + repo + "/contents/system_prompt.md"
        session = _get_session()
        gc.collect()
        headers = {"Authorization": "Bearer " + ai_key, "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
        resp = session.get(api_url, headers=headers)
        sha = ""
        if resp.status_code == 200:
            import json as _j
            sha = _j.loads(resp.text).get("sha", "")
        resp.close()
        gc.collect()
        # Push update
        body = {"message": "Update system_prompt.md", "content": b64}
        if sha:
            body["sha"] = sha
        resp = session.put(api_url, json=body, headers=headers)
        status = resp.status_code
        resp.close()
        del b64, content
        gc.collect()
        if status in (200, 201):
            return "ok"
        return "http " + str(status)
    except Exception as e:
        return str(e)


def _load_log():
    try:
        with open(LOG_PATH) as f:
            data = json.loads(f.read())
        if not isinstance(data, list):
            return []
        return data[-MAX_HISTORY:]
    except:
        return []

def _save_log(history):
    try:
        gc.collect()
        with open(LOG_PATH, "w") as f:
            f.write(json.dumps(history[-MAX_HISTORY:]))
    except Exception as e:
        print("AI log save error:", e)

def _build_messages(history, user_msg, tool_context=None):
    """Build messages for API call. Keeps context minimal for RAM.
    - System prompt (constant, in flash)
    - Last 4 history entries, truncated to 300 chars each
    - Current user message
    - Optional tool context from previous iteration
    """
    msgs = [{"role": "system", "content": _load_prompt()}]
    for entry in history[-4:]:
        c = entry["content"]
        if len(c) > 300:
            c = c[:300] + "..."
        msgs.append({"role": entry["role"], "content": c})
    msgs.append({"role": "user", "content": user_msg})
    if tool_context:
        msgs.append({"role": "assistant", "content": tool_context[0]})
        msgs.append({"role": "user", "content": tool_context[1]})
    return msgs

_session = None
def _get_session():
    global _session
    if _session is None:
        import adafruit_requests, adafruit_connection_manager, wifi, socketpool
        pool = socketpool.SocketPool(wifi.radio)
        ssl = adafruit_connection_manager.get_radio_ssl_context(wifi.radio)
        _session = adafruit_requests.Session(pool, ssl)
    return _session

def _api_call(messages, provider, key, model):
    session = _get_session()

    if provider == "anthropic":
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        sys_content = messages[0]["content"]
        chat_msgs = messages[1:]
        body = {
            "model": model,
            "max_tokens": 4096,
            "system": sys_content,
            "messages": chat_msgs,
        }
    elif provider == "gemini":
        url = "https://generativelanguage.googleapis.com/v1beta/models/" + model + ":generateContent?key=" + key
        headers = {"content-type": "application/json"}
        sys_content = messages[0]["content"]
        contents = []
        for m in messages[1:]:
            role = "user" if m["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": m["content"]}]})
        body = {
            "system_instruction": {"parts": [{"text": sys_content}]},
            "contents": contents,
            "generationConfig": {"maxOutputTokens": 4096},
        }
    else:  # openai, openrouter, github
        if provider == "openrouter":
            url = "https://openrouter.ai/api/v1/chat/completions"
        elif provider == "github":
            url = "https://models.github.ai/inference/chat/completions"
        else:
            url = "https://api.openai.com/v1/chat/completions"
        if provider == "github":
            headers = {
                "Authorization": "Bearer " + key,
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "content-type": "application/json",
            }
        else:
            headers = {
                "Authorization": "Bearer " + key,
                "content-type": "application/json",
            }
        body = {
            "model": model,
            "max_tokens": 4096,
            "messages": messages,
        }

    try:
        gc.collect()
        resp = session.post(url, json=body, headers=headers)
        status = resp.status_code
        raw = resp.text
        resp.close()
        del resp
        gc.collect()
        if status != 200:
            err = raw[:200] if raw else ("HTTP " + str(status))
            try:
                ed = json.loads(raw)
                e2 = ed.get("error", {})
                if isinstance(e2, dict):
                    err = e2.get("message", err)
                else:
                    err = str(e2)
            except:
                pass
            del raw
            gc.collect()
            return None, str(err)
        data = json.loads(raw)
        del raw
        gc.collect()
    except Exception as e:
        gc.collect()
        return None, str(e)

    try:
        if provider == "anthropic":
            text = data["content"][0]["text"]
        elif provider == "gemini":
            text = data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            text = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        del data
        gc.collect()
        return None, "Unexpected API response"

    del data
    gc.collect()
    return text, None

def _exec_tools(tool_calls):
    results = []
    for tc in tool_calls:
        tool = tc.get("tool", "")
        args = tc.get("args", {})
        try:
            if tool == "read_file":
                path = args["path"]
                with open(path) as f:
                    content = f.read(4000)
                sz = os.stat(path)[6]
                truncated = sz > 4000
                r = {"tool": tool, "path": path, "ok": True, "content": content, "size": sz}
                if truncated:
                    r["note"] = "Truncated at 4000 chars (file is %d bytes). Use run_code to read specific sections." % sz
                results.append(r)
            elif tool == "write_file":
                path = args["path"]
                if "b64" in args:
                    content = a2b_base64(args["b64"]).decode("utf-8")
                else:
                    content = args["content"]
                if path.endswith(".py"):
                    compile(content, path, "exec")
                with open(path, "w") as f:
                    f.write(content)
                results.append({"tool": tool, "path": path, "ok": True, "size": len(content)})
            elif tool == "patch_file":
                path = args["path"]
                old = args["old"]
                new = args["new"]
                with open(path) as f:
                    content = f.read()
                if old not in content:
                    results.append({"tool": tool, "path": path, "ok": False, "error": "old string not found"})
                elif content.count(old) > 1:
                    results.append({"tool": tool, "path": path, "ok": False, "error": "old string matches %d times, must be unique" % content.count(old)})
                else:
                    content = content.replace(old, new, 1)
                    if path.endswith(".py"):
                        compile(content, path, "exec")
                    with open(path, "w") as f:
                        f.write(content)
                    results.append({"tool": tool, "path": path, "ok": True, "size": len(content)})
                del content
                gc.collect()
            elif tool == "list_dir":
                path = args.get("path", "/")
                entries = []
                for name in os.listdir(path):
                    full = path.rstrip("/") + "/" + name
                    try:
                        os.listdir(full)
                        entries.append({"name": name + "/", "size": None})
                    except:
                        try:
                            sz = os.stat(full)[6]
                        except:
                            sz = None
                        entries.append({"name": name, "size": sz})
                results.append({"tool": tool, "path": path, "ok": True, "entries": entries})
            elif tool == "delete":
                path = args["path"]
                try:
                    os.remove(path)
                except:
                    os.rmdir(path)
                results.append({"tool": tool, "path": path, "ok": True})
            elif tool == "mkdir":
                path = args["path"]
                try:
                    os.mkdir(path)
                except OSError:
                    pass
                results.append({"tool": tool, "path": path, "ok": True})
            elif tool == "disk_usage":
                st = os.statvfs("/")
                total = st[1] * st[2]
                free = st[1] * st[3]
                used = total - free
                results.append({"tool": tool, "ok": True, "total": total, "used": used, "free": free})
            elif tool == "run_code":
                code = args.get("code", "")
                import io
                _buf = io.StringIO()
                def _print(*a, **k):
                    sep = k.get("sep", " ")
                    end = k.get("end", "\n")
                    _buf.write(sep.join(str(x) for x in a) + end)
                _g = dict(globals())
                _g["print"] = _print
                exec(code, _g)
                output = _buf.getvalue()
                _buf.close()
                del _g, _buf, _print
                if len(output) > 2000:
                    output = output[:2000] + "\n...[truncated]"
                results.append({"tool": tool, "ok": True, "output": output})
            elif tool == "restart":
                results.append({"tool": tool, "ok": True, "note": "Restarting now..."})
            else:
                results.append({"tool": tool, "ok": False, "error": "Unknown tool"})
        except Exception as e:
            results.append({"tool": tool, "ok": False, "error": str(e)})
    return results

def _parse_response(text):
    """Parse AI response text into (reply, tool_calls)."""
    try:
        clean = text.strip()
        if clean.startswith("```"):
            clean = clean.split("\n", 1)[1] if "\n" in clean else clean[3:]
            clean = clean.rsplit("```", 1)[0]
            clean = clean.strip()
        parsed = json.loads(clean)
        return parsed.get("reply", ""), parsed.get("tools", [])
    except:
        # Try to extract JSON object from mixed text
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            try:
                parsed = json.loads(text[start:end+1])
                return parsed.get("reply", ""), parsed.get("tools", [])
            except:
                pass
        # Return plain text as reply (don't dump raw JSON to user)
        clean = text.strip()
        if clean.startswith("{") and clean.endswith("}"):
            clean = "(AI returned malformed JSON — try rephrasing your request)"
        return clean, []

def _result_summary(r):
    """Build a concise summary of a single tool result."""
    t = r.get("tool", "?")
    if not r.get("ok"):
        return t + " FAILED: " + r.get("error", "?")
    if t == "disk_usage":
        return "disk: total=%d used=%d free=%d" % (r.get("total", 0), r.get("used", 0), r.get("free", 0))
    if t == "list_dir":
        ents = r.get("entries", [])
        parts = []
        for e in ents[:30]:
            if isinstance(e, dict):
                n = e.get("name", "?")
                s = e.get("size")
                parts.append(n + ("(%d)" % s if s is not None else ""))
            else:
                parts.append(str(e))
        return "ls %s: %s" % (r.get("path", "/"), ", ".join(parts))
    if t == "read_file":
        c = r.get("content", "")
        if len(c) > 300:
            c = c[:300] + "...[truncated]"
        return "read %s:\n%s" % (r.get("path", "?"), c)
    if t == "run_code":
        o = r.get("output", "")
        if len(o) > 300:
            o = o[:300] + "...[truncated]"
        return "run_code:\n%s" % o
    if t == "write_file":
        return "wrote %s (%d bytes)" % (r.get("path", "?"), r.get("size", 0))
    if t == "patch_file":
        return "patched %s (%d bytes)" % (r.get("path", "?"), r.get("size", 0))
    return t + " " + r.get("path", "") + " OK"

MAX_ITERATIONS = 5

def chat(user_msg, provider, key, model):
    history = _load_log()
    all_results = []
    should_restart = False
    reply_text = ""
    tool_context = None  # (assistant_text, tool_results_text) from previous iteration

    for iteration in range(MAX_ITERATIONS):
        gc.collect()
        # Rebuild messages fresh each iteration — never accumulate
        messages = _build_messages(history, user_msg, tool_context)
        text, err = _api_call(messages, provider, key, model)
        del messages
        gc.collect()

        if err:
            if iteration == 0:
                return {"reply": "API error: " + err, "tools": [], "results": []}
            reply_text = reply_text or ("API error on iteration %d: " % iteration + err)
            break

        reply_text, tool_calls = _parse_response(text)

        # Check for restart
        for tc in tool_calls:
            if tc.get("tool") == "restart":
                should_restart = True

        # No tools = done
        if not tool_calls:
            del text
            gc.collect()
            break

        # Execute tools
        results = _exec_tools(tool_calls)
        all_results.extend(results)

        if should_restart:
            del text
            gc.collect()
            break

        # Build compact context for next iteration (instead of growing messages)
        summaries = "; ".join(_result_summary(r) for r in results)
        if len(summaries) > 800:
            summaries = summaries[:800] + "..."
        tool_context = (text, "Tool results: " + summaries + "\nContinue. If done, respond with final answer and no tools. JSON only.")
        del text, results, summaries
        gc.collect()

    # Save to history (compact)
    history.append({"role": "user", "content": user_msg})
    summary = reply_text
    if all_results:
        s = "; ".join(_result_summary(r) for r in all_results)
        if len(s) > 500:
            s = s[:500] + "..."
        summary += "\n[" + s + "]"
    history.append({"role": "assistant", "content": summary})
    _save_log(history)
    del history
    gc.collect()

    if should_restart:
        import microcontroller
        microcontroller.reset()

    return {"reply": reply_text, "tools": [], "results": all_results}

def get_history():
    return _load_log()

def clear_history():
    try:
        os.remove(LOG_PATH)
    except:
        pass
    return True
