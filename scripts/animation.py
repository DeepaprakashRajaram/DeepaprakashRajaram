import os
import yaml
import xml.etree.ElementTree as ET

def load_config():
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def animate_svg(static_path, animated_path, config, variant_name):
    ET.register_namespace('', "http://www.w3.org/2000/svg")
    
    try:
        tree = ET.parse(static_path)
    except Exception as e:
        print(f"Error parsing {static_path}: {e}")
        return False
        
    root = tree.getroot()
    # Find the <g> element containing the text
    g_elem = None
    for child in root:
        if child.tag.endswith('g'):
            g_elem = child
            break
            
    if g_elem is None:
        print("Could not find <g> element in SVG.")
        return False
        
    anim_config = config.get("animation", {})
    profile = anim_config.get("profile", "article-default")
    
    if profile == "disabled":
        # Just copy it over
        tree.write(animated_path, encoding="utf-8", xml_declaration=True)
        return True
        
    if profile != "article-default":
        print(f"Animation profile {profile} is not yet implemented. Falling back to static.")
        tree.write(animated_path, encoding="utf-8", xml_declaration=True)
        return True
        
    # Implement article-default
    row_dur = anim_config.get("row_duration", 1.0)
    row_delay = anim_config.get("row_delay", 0.08)
    cursor_config = anim_config.get("cursor", {})
    cursor_enabled = cursor_config.get("enabled", True)
    cursor_color = cursor_config.get("color", "#000000")
    
    # SVG namespace string for element creation
    ns = "{http://www.w3.org/2000/svg}"
    
    # Create a <defs> block
    defs = ET.Element(f"{ns}defs")
    root.insert(0, defs)
    
    viewbox = root.attrib.get('viewBox', '0 0 800 600')
    try:
        svg_w = float(viewbox.split()[2])
    except:
        svg_w = 800.0
        
    # Support for light/dark mode SVGs
    # We will just apply the same logic to ALL <text> elements in the document sequentially
    # This naturally handles layered SVGs because the layers are ordered sequentially in the DOM
    
    # We need the master <g> element that wraps everything
    for child in root:
        if child.tag.endswith('g'):
            g_elem = child
            break
            
    # Find all text elements regardless of which layer <g> they are in
    texts = list(root.iter(f"{ns}text"))
    cursors = []
    
    for i, text_elem in enumerate(texts):
        y_pos = float(text_elem.attrib.get('y', 0))
        begin_time = i * row_delay
        clip_id = f"clip-{variant_name}-{i}"
        
        # 1. Create clipPath
        clip_path = ET.SubElement(defs, f"{ns}clipPath", id=clip_id)
        rect = ET.SubElement(clip_path, f"{ns}rect", x="0", y=str(y_pos - 12), width="0", height="15")
        
        # Determine if this is the eye layer for a special fade (eye is usually short and at the end)
        parent = text_elem.find('..')
        
        animate = ET.SubElement(rect, f"{ns}animate", 
                                attributeName="width", 
                                to=str(svg_w), 
                                dur=f"{row_dur}s", 
                                begin=f"{begin_time}s", 
                                fill="freeze")
        animate.set("from", "0") 
        
        # 2. Attach clipPath to text
        text_elem.set("clip-path", f"url(#{clip_id})")
        
        # 3. Create cursor if enabled
        if cursor_enabled:
            cursor = ET.Element(f"{ns}rect", 
                                x="0", 
                                y=str(y_pos - 12), 
                                width=str(7.74 * cursor_config.get("width_scale", 1.0)), 
                                height=str(15 * cursor_config.get("height_scale", 1.0)), 
                                fill=cursor_color, 
                                opacity="0")
            
            # Appear at start
            set_start = ET.SubElement(cursor, f"{ns}set", attributeName="opacity", to="1", begin=f"{begin_time}s")
            # Move across
            anim_x = ET.SubElement(cursor, f"{ns}animate", 
                                   attributeName="x", 
                                   to=str(svg_w), 
                                   dur=f"{row_dur}s", 
                                   begin=f"{begin_time}s", 
                                   fill="freeze")
            anim_x.set("from", "0")
            # Disappear at end
            set_end = ET.SubElement(cursor, f"{ns}set", attributeName="opacity", to="0", begin=f"{begin_time + row_dur}s", fill="freeze")
            
            cursors.append(cursor)
            
    # Add cursors to the root SVG or master <g> so they render on top
    for c in cursors:
        g_elem.append(c)
    
    tree.write(animated_path, encoding="utf-8", xml_declaration=True)
    return True

if __name__ == "__main__":
    config = load_config()
    for variant in config["hero_renderer"]["variants"]:
        preview_dir = os.path.join(config["paths"]["preview"], variant)
        
        # Animate light variant
        static_light = os.path.join(preview_dir, "10-hero-static-light.svg")
        animated_light = os.path.join(preview_dir, "11-hero-animated-light.svg")
        if os.path.exists(static_light):
            print(f"Animating {variant} (Light)...")
            animate_svg(static_light, animated_light, config, variant)
            
        # Animate dark variant
        static_dark = os.path.join(preview_dir, "10-hero-static-dark.svg")
        animated_dark = os.path.join(preview_dir, "11-hero-animated-dark.svg")
        if os.path.exists(static_dark):
            print(f"Animating {variant} (Dark)...")
            animate_svg(static_dark, animated_dark, config, variant)
            
        # Also handle standard static if it still exists (for other variants)
        static_path = os.path.join(preview_dir, "10-hero-static.svg")
        animated_path = os.path.join(preview_dir, "11-hero-animated.svg")
        if os.path.exists(static_path):
            print(f"Animating {variant}...")
            animate_svg(static_path, animated_path, config, variant)
