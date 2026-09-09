import argparse
import yaml
import os

import asset_prep
import hero_renderer
import animation
import validate_svg

def load_config():
    if not os.path.exists("config.yaml"):
        return {"project": {"version": "Unknown"}, "paths": {}}
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def main():
    parser = argparse.ArgumentParser(description="Profile Generator")
    parser.add_argument("--dry-run", action="store_true", help="Report what would happen without modifying anything")
    args = parser.parse_args()

    config = load_config()

    print(f"Profile Generator v{config['project']['version']}")
    
    if args.dry_run:
        print("\n[DRY-RUN] Running in dry-run mode. No files will be modified.")
        return

    print("--- 1. Asset Preparation ---")
    prep_path = asset_prep.prep_asset()
    
    print("\n--- 2. Static Rendering ---")
    # For phase 3, we generate all variants
    for variant in config["hero_renderer"]["variants"]:
        hero_renderer.render_variant(prep_path, config, variant)
        
    print("\n--- 3. Animation & Validation ---")
    for variant in config["hero_renderer"]["variants"]:
        preview_dir = os.path.join(config["paths"]["preview"], variant)
        static_path = os.path.join(preview_dir, "10-hero-static.svg")
        animated_path = os.path.join(preview_dir, "11-hero-animated.svg")
        
        if os.path.exists(static_path):
            print(f"Animating {variant}...")
            if animation.animate_svg(static_path, animated_path, config, variant):
                validate_svg.validate_svg(animated_path)
                
    print("\n--- 4. Profile Assembly ---")
    import fetch_stats
    import generate_headings
    import embed_fonts
    import build_readme
    
    print("Generating GitHub statistics...")
    fetch_stats.run()
    
    print("Generating SVG headings...")
    generate_headings.run()
    
    print("Embedding fonts...")
    embed_fonts.run()
    
    print("Building final README...")
    build_readme.run()
    
    import backup_manager
    print("\n--- 5. Tracking Assets for Rollback ---")
    for root, _, files in os.walk(preview_dir):
        for file in files:
            filepath = os.path.join(root, file)
            backup_manager.track_generated_file(filepath)
    backup_manager.track_generated_file("README.md")
    print("All generated assets tracked for safe rollback.")

    print("\nBaseline Implementation Complete. Previews are available in the preview/ directory.")

if __name__ == "__main__":
    main()
