import os
import yaml
from PIL import Image
from rembg import remove
import numpy as np

def load_config():
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def prep_asset():
    print("--- Asset Preparation ---")
    config = load_config()
    input_path = config["paths"]["hero_asset"]
    crop_percent = config["hero_renderer"]["crop_bottom_percent"]
    
    preview_dir = config["paths"]["preview"]
    os.makedirs(preview_dir, exist_ok=True)
    
    img = Image.open(input_path).convert("RGBA")
    
    # 1. Crop bottom text
    width, height = img.size
    crop_height = int(height * (1.0 - (crop_percent / 100.0)))
    img_cropped = img.crop((0, 0, width, crop_height))
    
    preview_crop_path = os.path.join(preview_dir, "00-cropped.png")
    img_cropped.save(preview_crop_path)
    print(f"Cropped bottom {crop_percent}%. Saved to {preview_crop_path}")
    
    # 2. Remove background
    print("Removing background using rembg...")
    # Convert PIL to numpy for rembg
    img_np = np.array(img_cropped)
    out_np = remove(img_np)
    img_no_bg = Image.fromarray(out_np)
    
    preview_bg_path = os.path.join(preview_dir, "01-bg-removed.png")
    img_no_bg.save(preview_bg_path)
    print(f"Background removed. Saved to {preview_bg_path}")
    
    # 3. Crop to bounding box of the non-transparent pixels to center it
    bbox = img_no_bg.getbbox()
    if bbox:
        img_centered = img_no_bg.crop(bbox)
    else:
        img_centered = img_no_bg # Fallback if empty
        
    preview_centered_path = os.path.join(preview_dir, "02-centered.png")
    img_centered.save(preview_centered_path)
    print(f"Emblem centered and whitespace removed. Saved to {preview_centered_path}")
    
    return preview_centered_path

if __name__ == "__main__":
    prep_asset()
