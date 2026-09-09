import os
import xml.etree.ElementTree as ET

def validate_svg(filepath):
    print(f"Validating {filepath}...")
    try:
        tree = ET.parse(filepath)
    except Exception as e:
        print(f"  [FAIL] Invalid XML: {e}")
        return False
        
    root = tree.getroot()
    ns = "{http://www.w3.org/2000/svg}"
    
    if root.tag != f"{ns}svg":
        print("  [FAIL] Not a valid SVG structure (missing svg root).")
        return False
        
    # Check for animation elements
    anim_elements = list(root.iter(f"{ns}animate")) + list(root.iter(f"{ns}set"))
    if not anim_elements:
        print("  [WARN] No SMIL animation elements found.")
    else:
        print(f"  [PASS] Found {len(anim_elements)} animation elements.")
        
    # Check for unique IDs
    ids = []
    for elem in root.iter():
        if 'id' in elem.attrib:
            ids.append(elem.attrib['id'])
            
    if len(ids) != len(set(ids)):
        print("  [FAIL] Duplicate IDs found.")
        return False
        
    print("  [PASS] All IDs are unique.")
    print("  [PASS] Validation successful.\n")
    return True

if __name__ == "__main__":
    import yaml
    with open("config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
        
    for variant in config["hero_renderer"]["variants"]:
        animated_path = os.path.join(config["paths"]["preview"], variant, "11-hero-animated.svg")
        if os.path.exists(animated_path):
            validate_svg(animated_path)
