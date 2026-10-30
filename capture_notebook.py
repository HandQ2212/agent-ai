"""Capture all executed notebook cells with one local Chrome DevTools session."""
from pathlib import Path
import base64
import json
import subprocess
import tempfile
import time
import urllib.request
import websocket

root = Path(__file__).resolve().parent
profile = Path(tempfile.mkdtemp(prefix="capture-", dir=root / "build"))
chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
pages = sorted((root / "screenshots").glob("cell_*.html"),
               key=lambda p: int(p.stem.split("_")[1]))
log = open(root / "build/chrome_capture.log", "w")
process = subprocess.Popen([
    chrome, "--headless", "--disable-gpu", "--no-sandbox", "--no-first-run",
    "--disable-background-networking", "--disable-crash-reporter",
    "--remote-debugging-port=0", "--remote-debugging-address=127.0.0.1",
    "--remote-allow-origins=*", f"--user-data-dir={profile}", "about:blank",
], stdout=log, stderr=log)
try:
    deadline = time.monotonic() + 30
    port_file = profile / "DevToolsActivePort"
    while not port_file.exists():
        if time.monotonic() > deadline or process.poll() is not None:
            raise RuntimeError("Chrome DevTools did not start; see build/chrome_capture.log")
        time.sleep(0.1)
    port = port_file.read_text().splitlines()[0]
    targets = json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/json"))
    target = next(t for t in targets if t["type"] == "page")
    ws = websocket.create_connection(target["webSocketDebuggerUrl"], timeout=20)
    serial = 0
    def command(method, params=None):
        global serial
        serial += 1
        ws.send(json.dumps(dict(id=serial, method=method, params=params or {})))
        while True:
            response = json.loads(ws.recv())
            if response.get("id") == serial:
                if "error" in response:
                    raise RuntimeError(response["error"])
                return response.get("result", {})
    command("Page.enable")
    command("Emulation.setDeviceMetricsOverride", dict(width=1160, height=2000,
                                                        deviceScaleFactor=1, mobile=False))
    for page in pages:
        command("Page.navigate", {"url": page.as_uri()})
        for _ in range(100):
            check = command("Runtime.evaluate", {"expression":
                "location.href === " + json.dumps(page.as_uri())
                + " && document.readyState === 'complete' && !!document.querySelector('main')",
                "returnByValue": True})
            if check["result"].get("value"):
                break
            time.sleep(0.05)
        else:
            raise RuntimeError(f"Page did not load: {page.name}")
        command("Runtime.evaluate", {"expression": "document.fonts.ready", "awaitPromise": True})
        bounds = command("Runtime.evaluate", {"expression":
            "({bottom: document.querySelector('main').getBoundingClientRect().bottom})",
            "returnByValue": True})["result"]["value"]
        clip = dict(x=20, y=120, width=1120, height=bounds["bottom"]-124, scale=1)
        screenshot = command("Page.captureScreenshot", dict(format="png", clip=clip,
                                                             captureBeyondViewport=True))
        target_path = page.with_suffix(".png")
        target_path.write_bytes(base64.b64decode(screenshot["data"]))
        print(f"Captured {target_path.name}: height={clip['height']:.0f}", flush=True)
    ws.close()
finally:
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
    log.close()
