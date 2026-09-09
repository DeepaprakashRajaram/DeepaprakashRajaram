import os
from PIL import Image

def validate_asset(filepath):
    print("--- Asset Validation ---")
    if not os.path.exists(filepath):
        print(f"ERROR: File does not exist at {filepath}")
        return False
    
    print(f"File exists: {filepath}")
    
    try:
        with Image.open(filepath) as img:
            print("File is readable.")
            print(f"Format: {img.format} (Confirmed PNG: {img.format == 'PNG'})")
            print(f"Dimensions: {img.width}x{img.height}")
            print(f"Color Mode: {img.mode}")
            
            # Check transparency
            has_alpha = 'A' in img.mode
            if has_alpha:
                # Check if alpha channel actually has transparent pixels
                alpha = img.getchannel('A')
                extrema = alpha.getextrema()
                if extrema[0] < 255:
                    print("Transparency: Present (Has transparent pixels)")
                else:
                    print("Transparency: Present (Alpha channel exists, but fully opaque)")
            else:
                print("Transparency: Not Present")
            
            return True
            
    except Exception as e:
        print(f"ERROR: Failed to read image: {e}")
        return False

if __name__ == "__main__":
    validate_asset("assets/input/logo.png")
