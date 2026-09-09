import os
import cv2
import numpy as np
from PIL import Image

def process_stage(image_bgr, stage_num, variant_name, step_name, preview_dir):
    path = os.path.join(preview_dir, f"{stage_num:02d}-{step_name}.png")
    cv2.imwrite(path, image_bgr)
    return image_bgr

def render_variant(img_path, config, variant_name):
    print(f"\nRendering variant: {variant_name}")
    params = config["hero_renderer"]["variants"][variant_name]
    
    preview_dir = os.path.join(config["paths"]["preview"], variant_name)
    os.makedirs(preview_dir, exist_ok=True)
    
    # 1. Load image (it's RGBA from prep)
    # Convert to BGR for OpenCV
    pil_img = Image.open(img_path).convert("RGBA")
    
    # Create white background to replace transparency
    white_bg = Image.new("RGBA", pil_img.size, "WHITE")
    white_bg.paste(pil_img, mask=pil_img)
    bgr_img = cv2.cvtColor(np.array(white_bg), cv2.COLOR_RGBA2BGR)
    
    process_stage(bgr_img, 3, variant_name, "white-bg", preview_dir)
    
    # 2. Noise Reduction & Edge Preservation
    d = params["bilateral_d"]
    sigma = params["bilateral_sigma"]
    smoothed = cv2.bilateralFilter(bgr_img, d, sigma, sigma)
    process_stage(smoothed, 4, variant_name, "smoothed", preview_dir)
    
    # Convert to Grayscale
    gray = cv2.cvtColor(smoothed, cv2.COLOR_BGR2GRAY)
    process_stage(gray, 5, variant_name, "grayscale", preview_dir)
    
    # 3. Contrast Enhancement
    clahe = cv2.createCLAHE(clipLimit=params["clahe_clip"], tileGridSize=(8,8))
    contrast = clahe.apply(gray)
    process_stage(contrast, 6, variant_name, "contrast", preview_dir)
    
    # 4. Brightness Mapping / Gamma Correction
    gamma = params["gamma"]
    inv_gamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
    gamma_corr = cv2.LUT(contrast, table)
    process_stage(gamma_corr, 7, variant_name, "gamma", preview_dir)
    
    # 5. ASCII Mapping
    cols = params["cols"]
    h, w = gamma_corr.shape
    # ASCII characters are about twice as tall as they are wide
    # Rows are cols * (h/w) * 0.48
    aspect_ratio = h / w
    rows = int(cols * aspect_ratio * 0.48)
    
    resized = cv2.resize(gamma_corr, (cols, rows), interpolation=cv2.INTER_AREA)
    process_stage(resized, 8, variant_name, "downscaled", preview_dir)
    
    ramp = params["ramp"]
    ramp_len = len(ramp)
    
    ascii_art = []
    unique_glyphs = set()
    for row in resized:
        ascii_row = ""
        for pixel in row:
            # Map pixel (0-255) to ramp index. White (255) -> space (if first char is space)
            # Actually, standard ASCII mapping: dark -> light characters, or vice versa depending on ramp
            # If the ramp is ' .:-=+*#%@', 0 is dark (needs '@'), 255 is white (needs ' ')
            # Let's map 0 to len-1 (darkest), 255 to 0 (lightest)
            # wait, if pixel is 255 (white), index should be 0 (space)
            # index = (255 - pixel) / 255 * (ramp_len - 1)
            idx = int(((255 - pixel) / 255.0) * (ramp_len - 1))
            char = ramp[idx]
            ascii_row += char
            unique_glyphs.add(char)
        ascii_art.append(ascii_row)
        
    with open(os.path.join(preview_dir, "09-ascii.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(ascii_art))
        
    # 6. SVG Generation
    svg_lines = []
    svg_w = cols * 7.74  # Approx width
    svg_h = rows * 15.0  # Approx height
    
    svg_lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="100%" height="100%">')
    # Background
    svg_lines.append(f'<rect width="100%" height="100%" fill="{config["hero_renderer"]["background_color"]}"/>')
    svg_lines.append(f'<g font-family="monospace" font-size="12.9px" fill="#000000">')
    
    for i, line in enumerate(ascii_art):
        y_pos = (i + 1) * 15.0
        
        # Text element
        # Encode XML special chars first!
        safe_line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        # Replace spaces with non-breaking spaces for SVG
        safe_line = safe_line.replace(' ', '&#160;')

        
        svg_lines.append(f'<text x="0" y="{y_pos}">{safe_line}</text>')
        
    svg_lines.append('</g>')
    svg_lines.append('</svg>')
    
    svg_path = os.path.join(preview_dir, "10-hero-static.svg")
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_lines))
        
    print(f"Metrics for {variant_name}:")
    print(f"  Dimensions: {cols}x{rows}")
    print(f"  Total characters: {cols * rows}")
    print(f"  Unique glyphs: {len(unique_glyphs)}")
    print(f"  Estimated SVG size: {os.path.getsize(svg_path) / 1024:.1f} KB")

if __name__ == "__main__":
    import yaml
    with open("config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    prep_path = os.path.join(config["paths"]["preview"], "02-centered.png")
    for variant in config["hero_renderer"]["variants"]:
        render_variant(prep_path, config, variant)
