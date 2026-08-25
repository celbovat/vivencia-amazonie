import subprocess, sys, re, html, pathlib
CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
css = pathlib.Path('styles.css').read_text()
h = ('<!doctype html><meta charset="utf-8"><style>' + css + '</style>'
     '<script>window.addEventListener("load",function(){'
     'var n=0;try{n=document.styleSheets[0].cssRules.length}catch(e){n=-1}'
     'var p=document.createElement("pre");p.id="d";p.textContent="rules="+n;'
     'document.body.appendChild(p);});</script><body></body>')
pathlib.Path('/tmp/_css.html').write_text(h)
r = subprocess.run([CH,"--headless","--disable-gpu","--virtual-time-budget=3000",
                    "--dump-dom","file:///tmp/_css.html"],capture_output=True,text=True)
m = re.search(r'<pre id="d">rules=(-?\d+)</pre>', r.stdout)
print("prohlížeč parsuje pravidel:", m.group(1) if m else "?")
hloubka=0; top=0
for ch in css:
    if ch=='{':
        if hloubka==0: top+=1
        hloubka+=1
    elif ch=='}': hloubka-=1
print("pravidel v souboru:", top)
