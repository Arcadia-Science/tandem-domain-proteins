import base64
import json
import os
import re
import urllib.request

VIEWER_URL = (
    "https://ajax.googleapis.com/ajax/libs/model-viewer/4.0.0/model-viewer.min.js"
)
FONT_URL = (
    "https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible+Next:ital,wght@0,"
    "400;0,700;1,400;1,700&display=swap"
)
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
TIMEOUT = 30

CONFIG = "gallery_config.json"
OUTPUT = "output/gallery.html"
TITLE = "Protein structures"


def log(msg):
    return print(msg, flush=True)


def b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def hex_to_linear(h):
    h = h.lstrip("#")
    srgb = [int(h[i: i + 2], 16) / 255.0 for i in (0, 2, 4)]
    return [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb]


def strip_tags(s):
    return re.sub(r"<[^>]+>", "", s)


def download(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return r.read()


def embed_font():
    log("  Downloading font …")
    css = download(FONT_URL, UA).decode()
    for url in re.findall(r"url\((https://[^)]+)\)", css):
        data = base64.b64encode(download(url, UA)).decode()
        ext = url.rsplit(".", 1)[-1]
        mime = {"woff2": "font/woff2", "woff": "font/woff", "ttf": "font/ttf"}.get(
            ext, "application/octet-stream"
        )
        css = css.replace(f"url({url})", f"url(data:{mime};base64,{data})")
    match = re.search(r"font-family:\s*['\"]([^'\"]+)['\"]", css)
    family = match.group(1) if match else "Atkinson Hyperlegible Next"
    log(f"  ✓ Font embedded ({family}).")
    return f"<style>\n{css}\n</style>", family


def embed_viewer():
    log("  Downloading model-viewer JS …")
    js = download(VIEWER_URL).decode()
    log("  ✓ Viewer embedded.")
    return f'<script type="module">\n{js}\n</script>'


def build():
    with open(CONFIG) as f:
        entries = json.load(f)

    log(f"Building gallery with {len(entries)} models …")
    viewer_script = embed_viewer()
    font_style, font_family = embed_font()

    viewers_html, menu_html, figures_js = "", "", ""

    for i, e in enumerate(entries):
        label, subtitle = e["label"], e.get("subtitle", "")
        pill = f"<strong>{label}</strong>" + (f" {subtitle}" if subtitle else "")
        alt = f"3D structure: {label} {strip_tags(subtitle)}".strip()
        glb = b64(e["glb"])
        log(f"  Embedded: {e['glb']}")

        active = " active" if i == 0 else ""
        viewers_html += (
            f'    <model-viewer class="viewer-layer{active}" data-glb="{glb}" '
            f'alt="{alt}" camera-controls auto-rotate shadow-intensity="1" '
            f'interaction-prompt="none"></model-viewer>\n'
        )

        menu_html += (
            f'            <div class="menu-item" onclick="selectItem(event,{i})">'
            f"{pill}</div>\n"
        )

        r, g, b = hex_to_linear(e["model_color"])
        mc = f"[{r},{g},{b},1]"
        bg = json.dumps(e.get("bg_color", "#ffffff"))
        figures_js += f"        {{pill_html:{json.dumps(pill)},model_color:{mc},bg_color:{bg}}},\n"

    first_pill = f"<strong>{entries[0]['label']}</strong>"
    if entries[0].get("subtitle"):
        first_pill += f" {entries[0]['subtitle']}"
    first_bg = entries[0].get("bg_color", "#ffffff")

    html_out = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{TITLE}</title>
{font_style}
{viewer_script}
<style>
*,*::before,*::after{{margin:0;padding:0;box-sizing:border-box}}
body,html{{width:100%;height:100%;overflow:hidden;font-family:"{font_family}","Helvetica Neue",
Helvetica,Arial,sans-serif;background:{first_bg};transition:background .4s ease-in-out}} 
.gallery-wrapper{{position:relative;width:100vw;height:100vh}} .viewer-layer{{
position:absolute;inset:0;width:100%;height:100%;opacity:0;pointer-events:none;transition:opacity 
.4s ease-in-out;z-index:1;outline:none}} .viewer-layer.active{{
opacity:1;pointer-events:auto;z-index:2}} .nav-wrapper{{
position:fixed;top:16px;left:16px;z-index:100;font-size:clamp(11px,2cqi,
20px);display:flex;align-items:center;filter:drop-shadow(0 4px 12px rgba(0,0,0,
.10));cursor:pointer;transition:filter .2s}} .nav-wrapper:hover{{filter:drop-shadow(0 8px 16px 
rgba(0,0,0,.14))}} .nav-pill{{background:#fff;border-radius:999px;padding:.75em 
1.3em;display:flex;align-items:center;gap:.6em;color:#333;font-weight:400;position:relative;z
-index:10}} .nav-pill strong{{font-weight:700}} .dropdown-arrow{{
width:1em;height:1em;opacity:.5;transition:transform .3s cubic-bezier(.2,.8,.2,1);flex-shrink:0}} 
.nav-wrapper.is-open .dropdown-arrow{{transform:rotate(180deg)}} .dropdown-menu{{
position:absolute;top:130%;left:0;min-width:100%;width:max-content;background:#fff;border-radius
:.8em;padding:.4em;opacity:0;transform:translateY(-10px);pointer-events:none;transition:all .2s 
cubic-bezier(.2,.8,.2,1);display:flex;flex-direction:column;gap:.1em;z-index:200;box-shadow:0 
10px 25px rgba(0,0,0,.12)}} .nav-wrapper.is-open .dropdown-menu{{opacity:1;transform:translateY(
0);pointer-events:auto}} .menu-item{{padding:.6em 
1.1em;border-radius:.5em;cursor:pointer;font-size:.9em;color:#444;transition:background 
.1s;white-space:nowrap}} .menu-item strong{{font-weight:700}} .menu-item:hover{{
background:#f5f5f5;color:#000}} .pagination-wrapper{{
position:fixed;bottom:16px;right:16px;z-index:100;font-size:clamp(12px,2cqi,
24px);filter:drop-shadow(0 4px 12px rgba(0,0,0,.10))}} .pagination-pill{{
background:#fff;border-radius:999px;padding:.5em .8em;display:flex;align-items:center;gap:.8em}} 
.nav-btn{{cursor:pointer;display:flex;align-items:center;justify-content:center;border-radius:50
%;width:2em;height:2em;transition:background .15s,color 
.15s;color:#444;user-select:none;outline:none;-webkit-tap-highlight-color:transparent}} 
.nav-btn:hover{{background:#f0f0f0;color:#000}} .nav-btn svg{{width:1.5em;height:1.5em}} 
.pagination-wrapper::before{{content:'';position:absolute;top:50%;left:50%;transform:translate(
-50%,-50%);width:calc(100% - 4px);height:calc(100% - 
4px);border-radius:999px;z-index:-1;box-shadow:0 0 0 0 rgba(0,0,0,.1);animation:pulse 3s 
infinite}} @keyframes pulse{{0%{{box-shadow:0 0 0 0 rgba(0,0,0,.1)}}70%{{box-shadow:0 0 0 1em 
rgba(0,0,0,0)}}100%{{box-shadow:0 0 0 0 rgba(0,0,0,0)}}}} </style> </head> <body> <div 
class="gallery-wrapper"> <div class="nav-wrapper" id="navWrapper" onclick="toggleMenu(event)"> 
<div class="nav-pill"> <span id="currentLabel">{first_pill}</span> <svg class="dropdown-arrow" 
viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" 
stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg> </div> <div 
class="dropdown-menu"> {menu_html}        </div> </div> <div class="pagination-wrapper"> <div 
class="pagination-pill"> <div class="nav-btn" onclick="prevModel(event)"><svg viewBox="0 0 24 24" 
fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" 
stroke-linejoin="round"><polyline points="15 18 9 12 15 6"/></svg></div> <div class="nav-btn" 
onclick="nextModel(event)"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" 
stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 
6"/></svg></div> </div> </div> {viewers_html}</div>
<script type="module">
    const F=[
{figures_js}    ];
    const nav=document.getElementById('navWrapper'),lbl=document.getElementById('currentLabel'),
          V=document.querySelectorAll('.viewer-layer');
    let cur=0;const loaded=new Set;

    async function hydrate(i){{ if(loaded.has(i))return; loaded.add(i); const el=V[i],
    d=el.dataset.glb; if(d){{ await new Promise(r=>setTimeout(r,10)); const res=await fetch(
    'data:model/gltf-binary;base64,'+d); const blob=await res.blob(); el.setAttribute('src',
    URL.createObjectURL(blob)); el.removeAttribute('data-glb'); }} if(F[
    i].model_color)el.addEventListener('load',()=>{{ for(const m of 
    el.model.materials)m.pbrMetallicRoughness.setBaseColorFactor(F[i].model_color); }},
    {{once:true}}); }}

    async function go(i){{
        document.body.style.background=F[i].bg_color;
        V.forEach((v,j)=>{{if(j===i)v.classList.add('active');else v.classList.remove('active')}});
        lbl.innerHTML=F[i].pill_html;
        await hydrate(i);
        hydrate((i+1)%F.length);
        hydrate((i-1+F.length)%F.length);
    }}

    window.toggleMenu=e=>{{e.stopPropagation();nav.classList.toggle('is-open')}};
    window.selectItem=(e,i)=>{{e.stopPropagation();cur=i;go(i);nav.classList.remove('is-open')}};
    window.nextModel=e=>{{if(e)e.stopPropagation();cur=(cur+1)%F.length;go(cur)}};
    window.prevModel=e=>{{if(e)e.stopPropagation();cur=(cur-1+F.length)%F.length;go(cur)}};
    document.addEventListener('click',e=>{{if(!nav.contains(e.target))nav.classList.remove('is-open')}});
    document.addEventListener('keydown',e=>{{if(e.key==='ArrowRight')nextModel(e);if(e.key==='ArrowLeft')prevModel(e)}});
    go(0);
</script>
</body>
</html>"""

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)

    with open(OUTPUT, "w") as f:
        f.write(html_out)
    log(f"Created '{OUTPUT}' ({os.path.getsize(OUTPUT) / 1048576:.1f} MB)")


if __name__ == "__main__":
    build()
