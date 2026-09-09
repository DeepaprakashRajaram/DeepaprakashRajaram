import os
import yaml

def load_config():
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def run():
    config = load_config()
    preview_dir = config["paths"]["preview"]
    variant = config["hero_renderer"]["default_variant"]
    username = config["project"]["username"]
    
    hero_svg_path = f"{variant}/11-hero-animated.svg"
    stats_svg_path = "12-stats.svg"
    
    readme_content = f"""<p align="center">
  <img src="preview/{hero_svg_path}" alt="Hero Animation" width="100%">
</p>

# <img src="preview/headings/about_me.svg" alt="About Me" height="35">

Hi, I'm {username}. I am passionate about software engineering, system architecture, and automation. This GitHub profile is self-generating and fully automated using Python and GitHub Actions.

# <img src="preview/headings/statistics.svg" alt="Statistics" height="35">

<p align="left">
  <img src="preview/{stats_svg_path}" alt="{username}'s GitHub Statistics">
</p>

# <img src="preview/headings/projects.svg" alt="Projects" height="35">

- **[GitHub Profile Generator](https://github.com/{username}/{username})**: The very repository you are looking at! A deterministic, configuration-driven, self-generating profile featuring custom ASCII SVG animations.

# <img src="preview/headings/connect.svg" alt="Connect" height="35">

Feel free to reach out or explore my repositories above.
"""

    readme_path = "README.md"
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)
    print(f"Assembled final README at {readme_path}")

if __name__ == "__main__":
    run()
