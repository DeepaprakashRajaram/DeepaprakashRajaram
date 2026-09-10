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
        
        # Helper to process a variant file if it exists
        def process_variant_svg(suffix):
            static_p = os.path.join(preview_dir, f"10-hero-static{suffix}.svg")
            animated_p = os.path.join(preview_dir, f"11-hero-animated{suffix}.svg")
            if os.path.exists(static_p):
                print(f"Animating {variant}{suffix}...")
                if animation.animate_svg(static_p, animated_p, config, variant):
                    validate_svg.validate_svg(animated_p)
                    
        process_variant_svg("-light")
        process_variant_svg("-dark")
        process_variant_svg("")
                
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
