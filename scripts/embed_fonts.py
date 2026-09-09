import os
import base64
import yaml
import xml.etree.ElementTree as ET

def load_config():
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def get_font_base64(font_path):
    if not os.path.exists(font_path):
        return None
    with open(font_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def inject_font(svg_path, font_b64, font_ext):
    if not font_b64:
        return

    try:
        ET.register_namespace('', "http://www.w3.org/2000/svg")
        tree = ET.parse(svg_path)
        root = tree.getroot()
        ns = "{http://www.w3.org/2000/svg}"
        
        # Check if defs exists
        defs = root.find(f"{ns}defs")
        if defs is None:
            defs = ET.Element(f"{ns}defs")
            root.insert(0, defs)
            
        style = ET.SubElement(defs, f"{ns}style")
        mime = "font/woff2" if font_ext == "woff2" else "font/ttf"
        style.text = f"@font-face {{ font-family: 'CustomFont'; src: url(data:{mime};charset=utf-8;base64,{font_b64}) format('{font_ext}'); }}"
        
        # Replace monospace with CustomFont
        for elem in root.iter():
            if 'font-family' in elem.attrib and elem.attrib['font-family'] == 'monospace':
                elem.attrib['font-family'] = "'CustomFont', monospace"
                
        tree.write(svg_path, encoding="utf-8", xml_declaration=True)
        print(f"Injected embedded font into {svg_path}")
    except Exception as e:
        print(f"Failed to inject font into {svg_path}: {e}")

def run():
    config = load_config()
    fonts_dir = config["paths"].get("fonts_dir", "assets/input/fonts")
    
    # Find a font
    font_path = None
    font_ext = None
    if os.path.exists(fonts_dir):
        for f in os.listdir(fonts_dir):
            if f.endswith(".woff2"):
                font_path = os.path.join(fonts_dir, f)
                font_ext = "woff2"
                break
            elif f.endswith(".ttf"):
                font_path = os.path.join(fonts_dir, f)
                font_ext = "ttf"
                break
                
    if not font_path:
        print(f"No .woff2 or .ttf font found in {fonts_dir}. Skipping font embedding.")
        return
        
    font_b64 = get_font_base64(font_path)
    
    # Inject into SVGs
    preview_dir = config["paths"]["preview"]
    
    # Headings
    headings_dir = os.path.join(preview_dir, "headings")
    if os.path.exists(headings_dir):
        for f in os.listdir(headings_dir):
            if f.endswith(".svg"):
                inject_font(os.path.join(headings_dir, f), font_b64, font_ext)
                
    # Stats
    stats_svg = os.path.join(preview_dir, "12-stats.svg")
    if os.path.exists(stats_svg):
        inject_font(stats_svg, font_b64, font_ext)
        
    # Animated Hero
    for variant in config["hero_renderer"]["variants"]:
        hero_anim = os.path.join(preview_dir, variant, "11-hero-animated.svg")
        if os.path.exists(hero_anim):
            inject_font(hero_anim, font_b64, font_ext)

if __name__ == "__main__":
    run()
