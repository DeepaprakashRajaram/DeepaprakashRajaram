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
        print("[WARN] No GITHUB_TOKEN provided. Statistics unavailable.")
        return None

    url = "https://api.github.com/graphql"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    stars = 0
    commits = 0
    prs = 0
    issues = 0
    has_next_page = True
    cursor = None
    
    try:
        while has_next_page:
            cursor_arg = f', after: "{cursor}"' if cursor else ""
            query = f"""
            query($login: String!) {{
              user(login: $login) {{
                contributionsCollection {{
                  totalCommitContributions
                  totalPullRequestContributions
                  totalIssueContributions
                }}
                repositories(first: 100, ownerAffiliations: OWNER, isFork: false{cursor_arg}) {{
                  pageInfo {{
                    hasNextPage
                    endCursor
                  }}
                  nodes {{
                    stargazerCount
                  }}
                }}
              }}
            }}
            """
            
            data = json.dumps({"query": query, "variables": {"login": username}}).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers=headers)
            with urllib.request.urlopen(req) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                
                user_data = res_data.get("data", {}).get("user", {})
                contrib = user_data.get("contributionsCollection", {})
                repos_data = user_data.get("repositories", {})
                repos = repos_data.get("nodes", [])
                
                # Only need to read contributions once
                if cursor is None:
                    commits = contrib.get("totalCommitContributions", 0)
                    prs = contrib.get("totalPullRequestContributions", 0)
                    issues = contrib.get("totalIssueContributions", 0)
                    
                stars += sum(repo.get("stargazerCount", 0) for repo in repos)
                
                page_info = repos_data.get("pageInfo", {})
                has_next_page = page_info.get("hasNextPage", False)
                cursor = page_info.get("endCursor")
                
        return {
            "stars": stars,
            "commits": commits,
            "prs": prs,
            "issues": issues
        }
    except Exception as e:
        print(f"[ERROR] Failed to fetch GitHub stats: {e}")
        return None

def generate_stats_svg(stats, config, output_path):
    stats_config = config.get("statistics", {})
    colors = stats_config.get("colors", {"background": "#FFFFFF", "text": "#000000", "accent": "#0366D6"})
    
    # Very simple static layout matching article aesthetic (monospace, matching colors)
    if stats is None:
        if os.path.exists(output_path):
            print(f"Stats unavailable, but preserving existing SVG at {output_path}")
            return
        
        import sys
        print(f"[FATAL] GitHub API failed and no previous statistics SVG exists at {output_path}. Failing workflow to prevent publishing incomplete profile.")
        sys.exit(1)
    else:
        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="400" height="150" viewBox="0 0 400 150">
    <rect width="100%" height="100%" fill="{colors['background']}" rx="6" />
    <g font-family="monospace" font-size="14" fill="{colors['text']}">
        <text x="20" y="30" font-weight="bold" font-size="16">GitHub Statistics</text>
        
        <text x="20" y="60">Total Stars:</text>
        <text x="180" y="60" fill="{colors['accent']}" font-weight="bold">{stats['stars']}</text>
        
        <text x="20" y="85">Commits (1y):</text>
        <text x="180" y="85" fill="{colors['accent']}" font-weight="bold">{stats['commits']}</text>
        
        <text x="20" y="110">Pull Requests (1y):</text>
        <text x="180" y="110" fill="{colors['accent']}" font-weight="bold">{stats['prs']}</text>
        
        <text x="20" y="135">Issues (1y):</text>
        <text x="180" y="135" fill="{colors['accent']}" font-weight="bold">{stats['issues']}</text>
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
