import os
import json
import urllib.request
import urllib.error
import yaml

def load_config():
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def fetch_github_stats(username, token):
    if not token:
        print("[WARN] No GITHUB_TOKEN provided. Generating placeholder statistics.")
        return {"stars": 1234, "commits": 5678, "prs": 90, "issues": 12}

    query = """
    query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          totalCommitContributions
          totalPullRequestContributions
          totalIssueContributions
        }
        repositories(first: 100, ownerAffiliations: OWNER, isFork: false) {
          nodes {
            stargazerCount
          }
        }
      }
    }
    """
    
    url = "https://api.github.com/graphql"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = json.dumps({"query": query, "variables": {"login": username}}).encode("utf-8")
    
    try:
        req = urllib.request.Request(url, data=data, headers=headers)
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            
            user_data = res_data.get("data", {}).get("user", {})
            contrib = user_data.get("contributionsCollection", {})
            repos = user_data.get("repositories", {}).get("nodes", [])
            
            stars = sum(repo.get("stargazerCount", 0) for repo in repos)
            commits = contrib.get("totalCommitContributions", 0)
            prs = contrib.get("totalPullRequestContributions", 0)
            issues = contrib.get("totalIssueContributions", 0)
            
            return {
                "stars": stars,
                "commits": commits,
                "prs": prs,
                "issues": issues
            }
    except Exception as e:
        print(f"[ERROR] Failed to fetch GitHub stats: {e}")
        return {"stars": 0, "commits": 0, "prs": 0, "issues": 0}

def generate_stats_svg(stats, config, output_path):
    stats_config = config.get("statistics", {})
    colors = stats_config.get("colors", {"background": "#FFFFFF", "text": "#000000", "accent": "#0366D6"})
    
    # Very simple static layout matching article aesthetic (monospace, matching colors)
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="400" height="150" viewBox="0 0 400 150">
    <rect width="100%" height="100%" fill="{colors['background']}" rx="6" />
    <g font-family="monospace" font-size="14" fill="{colors['text']}">
        <text x="20" y="30" font-weight="bold" font-size="16">GitHub Statistics</text>
        
        <text x="20" y="60">Total Stars:</text>
        <text x="150" y="60" fill="{colors['accent']}" font-weight="bold">{stats['stars']}</text>
        
        <text x="20" y="85">Commits (1y):</text>
        <text x="150" y="85" fill="{colors['accent']}" font-weight="bold">{stats['commits']}</text>
        
        <text x="20" y="110">Pull Requests:</text>
        <text x="150" y="110" fill="{colors['accent']}" font-weight="bold">{stats['prs']}</text>
        
        <text x="20" y="135">Issues:</text>
        <text x="150" y="135" fill="{colors['accent']}" font-weight="bold">{stats['issues']}</text>
    </g>
</svg>"""

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Generated statistics SVG at {output_path}")

def run():
    config = load_config()
    if not config.get("statistics", {}).get("enabled", True):
        print("Statistics module disabled in config. Skipping.")
        return
        
    username = config["project"]["username"]
    token = os.environ.get("GITHUB_TOKEN")
    
    stats = fetch_github_stats(username, token)
    
    preview_dir = config["paths"]["preview"]
    output_path = os.path.join(preview_dir, "12-stats.svg")
    generate_stats_svg(stats, config, output_path)

if __name__ == "__main__":
    run()
