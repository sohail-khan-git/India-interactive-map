# create_india_map.py
# Requires: pip install folium requests

import json
import os
import sys
import subprocess
from pathlib import Path

# Ensure required packages
try:
    import folium
    from folium.features import GeoJsonTooltip, GeoJsonPopup
except Exception:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "folium"], stdout=subprocess.DEVNULL)
    import folium
    from folium.features import GeoJsonTooltip, GeoJsonPopup

GEOJSON_URL = "https://raw.githubusercontent.com/geohacker/india/master/state/india_state.geojson"
OUT_GEOJSON = "india_states.geojson"
OUT_HTML = "india_map.html"

def try_download(url, out_path):
    try:
        import requests
    except Exception:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"], stdout=subprocess.DEVNULL)
        import requests
    try:
        r = requests.get(url, timeout=20)
        if r.status_code == 200 and r.content.strip():
            with open(out_path, "wb") as f:
                f.write(r.content)
            return True
        return False
    except Exception as e:
        print("Download failed:", e)
        return False

# If user already has local file, prefer it
if Path(OUT_GEOJSON).exists():
    print("Using local GeoJSON:", OUT_GEOJSON)
    with open(OUT_GEOJSON, "r", encoding="utf-8") as f:
        geojson = json.load(f)
else:
    print("Attempting to download GeoJSON from the web...")
    ok = try_download(GEOJSON_URL, OUT_GEOJSON)
    if ok:
        print("Downloaded GeoJSON to", OUT_GEOJSON)
        with open(OUT_GEOJSON, "r", encoding="utf-8") as f:
            geojson = json.load(f)
    else:
        print("Could not download GeoJSON. Creating a small demo GeoJSON instead.")
        geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {"STATE_NAME": "Demo-State-A"},
                    "geometry": {"type": "Polygon", "coordinates": [[[68,25],[75,25],[75,30],[68,30],[68,25]]]}
                },
                {
                    "type": "Feature",
                    "properties": {"STATE_NAME": "Demo-State-B"},
                    "geometry": {"type": "Polygon", "coordinates": [[[75,18],[82,18],[82,23],[75,23],[75,18]]]}
                },
                {
                    "type": "Feature",
                    "properties": {"STATE_NAME": "Demo-State-C"},
                    "geometry": {"type": "Polygon", "coordinates": [[[80,10],[88,10],[88,15],[80,15],[80,10]]]}
                }
            ]
        }
        with open(OUT_GEOJSON, "w", encoding="utf-8") as f:
            json.dump(geojson, f)

# Select which property contains state name
def pick_state_key(fc):
    f = fc.get("features", [])
    if not f:
        return None
    props = f[0].get("properties", {})
    candidates = ["st_nm", "STATE_NAME", "state", "NAME_1", "ST_NM", "State_Name", "State", "NAME"]
    for c in candidates:
        if c in props:
            return c
    return list(props.keys())[0] if props else None

state_key = pick_state_key(geojson)
print("State property key:", state_key)

# Build folium map
m = folium.Map(location=[22.0, 80.0], zoom_start=5, tiles="cartodbpositron")

def style_fn(feature):
    return {"fillColor": "#ffffff", "color": "#444444", "weight": 1, "fillOpacity": 0.6}

def highlight_fn(feature):
    return {"fillColor": "#ffeb3b", "color": "#000000", "weight": 2, "fillOpacity": 0.8}

tooltip = GeoJsonTooltip(fields=[state_key] if state_key else [], aliases=["State:"])
popup = GeoJsonPopup(fields=[state_key] if state_key else [], aliases=["State:"])

gj = folium.GeoJson(geojson, name="India States", style_function=style_fn, highlight_function=highlight_fn, tooltip=tooltip)
gj.add_child(popup)
gj.add_to(m)
folium.LayerControl().add_to(m)

m.save(OUT_HTML)
print("Map saved to", OUT_HTML)
print("Open it in your browser to hover over states and see state names.")
