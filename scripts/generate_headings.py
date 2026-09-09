import os
import yaml

def load_config():
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def generate_heading(text, output_path, config):
    stats_config = config.get("statistics", {})
    colors = stats_config.get("colors", {"background": "#FFFFFF", "text": "#000000"})
    
    # We create a simple, clean SVG heading
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="600" height="50" viewBox="0 0 600 50">
    <g font-family="monospace" font-size="24" font-weight="bold" fill="{colors['text']}">
        <text x="0" y="35">{text}</text>
    </g>
</svg>"""

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Generated heading '{text}' at {output_path}")

def run():
    config = load_config()
    headings = ["About Me", "Statistics", "Projects", "Connect"]
    
    preview_dir = os.path.join(config["paths"]["preview"], "headings")
    os.makedirs(preview_dir, exist_ok=True)
    
    for heading in headings:
        filename = heading.lower().replace(" ", "_") + ".svg"
        generate_heading(heading, os.path.join(preview_dir, filename), config)

if __name__ == "__main__":
    run()
