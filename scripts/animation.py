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
        
    # Find all <text> elements
    texts = g_elem.findall(f"{ns}text")
    
    # We need to collect the new elements to add them after the text elements,
    # or wrap them. Actually, cursor should be drawn ON TOP of the text, so add to <g> after.
    cursors = []
    
    for i, text_elem in enumerate(texts):
        y_pos = float(text_elem.attrib.get('y', 0))
        begin_time = i * row_delay
        clip_id = f"clip-{variant_name}-{i}"
        
        # 1. Create clipPath
        clip_path = ET.SubElement(defs, f"{ns}clipPath", id=clip_id)
        rect = ET.SubElement(clip_path, f"{ns}rect", x="0", y=str(y_pos - 12), width="0", height="15")
        
        animate = ET.SubElement(rect, f"{ns}animate", 
                                attributeName="width", 
                                frm="0", # 'from' is a Python keyword, ET handles 'from' via kwarg unpacking or we just use set
                                to=str(svg_w), 
                                dur=f"{row_dur}s", 
                                begin=f"{begin_time}s", 
                                fill="freeze")
        animate.set("from", "0") # workaround for reserved keyword
        
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
            
    # Append cursors to the end of <g> so they render on top
    for c in cursors:
        g_elem.append(c)
        
    tree.write(animated_path, encoding="utf-8", xml_declaration=True)
    return True

if __name__ == "__main__":
    config = load_config()
    for variant in config["hero_renderer"]["variants"]:
        preview_dir = os.path.join(config["paths"]["preview"], variant)
        static_path = os.path.join(preview_dir, "10-hero-static.svg")
        animated_path = os.path.join(preview_dir, "11-hero-animated.svg")
        if os.path.exists(static_path):
            print(f"Animating {variant}...")
            animate_svg(static_path, animated_path, config, variant)
