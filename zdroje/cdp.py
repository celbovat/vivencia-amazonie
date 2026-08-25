# -*- coding: utf-8 -*-
"""Minimalni klient DevTools protokolu.

Chrome 139 uz nepodporuje --dump-dom (overeno i na triviani strance),
takze se stranka ridi pres remote debugging port. Jen standardni knihovna.
"""
import base64, json, os, socket, struct, subprocess, time, urllib.request

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


class WS:
    def __init__(self, url):
        bez = url.split("://", 1)[1]
        hostport, _, cesta = bez.partition("/")
        host, _, port = hostport.partition(":")
        self.s = socket.create_connection((host, int(port or 80)), timeout=30)
        klic = base64.b64encode(os.urandom(16)).decode()
        self.s.sendall(("GET /%s HTTP/1.1\r\nHost: %s\r\nUpgrade: websocket\r\n"
                        "Connection: Upgrade\r\nSec-WebSocket-Key: %s\r\n"
                        "Sec-WebSocket-Version: 13\r\n\r\n"
                        % (cesta, hostport, klic)).encode())
        hlav = b""
        while b"\r\n\r\n" not in hlav:
            hlav += self.s.recv(1)
        assert b"101" in hlav.split(b"\r\n")[0], hlav[:200]
        self.zbytek = b""

    def _prijmi(self, n):
        while len(self.zbytek) < n:
            d = self.s.recv(65536)
            if not d:
                raise IOError("spojení zavřeno")
            self.zbytek += d
        v, self.zbytek = self.zbytek[:n], self.zbytek[n:]
        return v

    def posli(self, obj):
        data = json.dumps(obj).encode()
        maska = os.urandom(4)
        n = len(data)
        if n < 126:
            hlav = struct.pack("!BB", 0x81, 0x80 | n)
        elif n < 65536:
            hlav = struct.pack("!BBH", 0x81, 0x80 | 126, n)
        else:
            hlav = struct.pack("!BBQ", 0x81, 0x80 | 127, n)
        telo = bytes(b ^ maska[i % 4] for i, b in enumerate(data))
        self.s.sendall(hlav + maska + telo)

    def cti(self):
        b1, b2 = struct.unpack("!BB", self._prijmi(2))
        n = b2 & 0x7F
        if n == 126:
            n = struct.unpack("!H", self._prijmi(2))[0]
        elif n == 127:
            n = struct.unpack("!Q", self._prijmi(8))[0]
        if b2 & 0x80:
            m = self._prijmi(4)
            d = bytes(x ^ m[i % 4] for i, x in enumerate(self._prijmi(n)))
        else:
            d = self._prijmi(n)
        return json.loads(d.decode("utf-8", "replace"))


class Prohlizec:
    def __init__(self, url, port=9333, sirka=1280, vyska=900):
        self.port = port
        profil = "/tmp/_cdp_profil_%d" % port
        subprocess.run(["rm", "-rf", profil])
        self.p = subprocess.Popen(
            [CHROME, "--headless", "--disable-gpu", "--mute-audio", "--no-first-run",
             "--disable-background-networking", "--disable-component-update",
             "--user-data-dir=" + profil,
             "--window-size=%d,%d" % (sirka, vyska),
             "--remote-debugging-port=%d" % port, url],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        cil = None
        for _ in range(120):
            time.sleep(0.5)
            try:
                seznam = json.loads(urllib.request.urlopen(
                    "http://127.0.0.1:%d/json/list" % port, timeout=3).read())
                for t in seznam:
                    if t.get("type") == "page" and t.get("webSocketDebuggerUrl"):
                        cil = t
                        break
                if cil:
                    break
            except Exception:
                pass
        if not cil:
            raise RuntimeError("Chrome nenaběhl na portu %d" % port)
        self.ws = WS(cil["webSocketDebuggerUrl"])
        self.id = 0
        self.udalosti = []

    def volej(self, metoda, **par):
        self.id += 1
        self.ws.posli({"id": self.id, "method": metoda, "params": par})
        while True:
            o = self.ws.cti()
            if o.get("id") == self.id:
                if "error" in o:
                    raise RuntimeError("%s: %s" % (metoda, o["error"]))
                return o.get("result", {})
            if "method" in o:
                self.udalosti.append(o)

    def nasbirane(self, sekund=1.5):
        """Docte udalosti, ktere Chrome poslal sam od sebe."""
        puvodni = self.ws.s.gettimeout()
        self.ws.s.settimeout(sekund)
        try:
            while True:
                o = self.ws.cti()
                if "method" in o:
                    self.udalosti.append(o)
        except Exception:
            pass
        finally:
            self.ws.s.settimeout(puvodni)
        v, self.udalosti = self.udalosti, []
        return v

    def js(self, vyraz, cekat=True):
        r = self.volej("Runtime.evaluate", expression=vyraz,
                       returnByValue=True, awaitPromise=cekat,
                       userGesture=True)
        if "exceptionDetails" in r:
            raise RuntimeError(json.dumps(r["exceptionDetails"])[:500])
        return r.get("result", {}).get("value")

    def cekej(self, podminka, sekund=30):
        do = time.time() + sekund
        while time.time() < do:
            try:
                if self.js(podminka, cekat=False):
                    return True
            except Exception:
                pass
            time.sleep(0.3)
        return False

    def zavri(self):
        try:
            self.p.terminate()
            self.p.wait(timeout=10)
        except Exception:
            self.p.kill()
