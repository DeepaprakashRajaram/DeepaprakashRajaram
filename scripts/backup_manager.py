import os
import json
import datetime
import hashlib
import shutil

BACKUP_DIR = ".backup"
MANIFEST_FILE = os.path.join(BACKUP_DIR, "manifest.json")
GENERATOR_VERSION = "0.1.0"

def get_hash(filepath):
    if not os.path.exists(filepath):
        return None
    with open(filepath, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def init_manifest():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    if not os.path.exists(MANIFEST_FILE):
        with open(MANIFEST_FILE, "w") as f:
            json.dump({
                "generator_version": GENERATOR_VERSION,
                "created_at": datetime.datetime.now().isoformat(),
                "backups": {},
                "generated_files": {},
                "generated_dirs": [],
                "project_files": []
            }, f, indent=4)

def load_manifest():
    init_manifest()
    with open(MANIFEST_FILE, "r") as f:
        return json.load(f)

def save_manifest(manifest):
    with open(MANIFEST_FILE, "w") as f:
        json.dump(manifest, f, indent=4)

def backup_file(filepath, dry_run=False):
    if not os.path.exists(filepath):
        return
    manifest = load_manifest()
    if filepath in manifest["backups"]:
        return

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    backup_name = f"{filepath.replace('/', '_').replace(os.sep, '_')}.{timestamp}.bak"
    backup_path = os.path.join(BACKUP_DIR, backup_name)
    
    if dry_run:
        print(f"[DRY-RUN] Would backup {filepath} to {backup_path}")
        return

    shutil.copy2(filepath, backup_path)
    manifest["backups"][filepath] = {
        "backup_path": backup_path,
        "original_hash": get_hash(filepath),
        "timestamp": datetime.datetime.now().isoformat()
    }
    save_manifest(manifest)
    print(f"Backed up {filepath} to {backup_path}")

def track_generated_file(filepath, dry_run=False):
    manifest = load_manifest()
    if filepath not in manifest["generated_files"]:
        if dry_run:
            print(f"[DRY-RUN] Would track generated file: {filepath}")
            return
        manifest["generated_files"][filepath] = {
            "timestamp": datetime.datetime.now().isoformat(),
            "hash": get_hash(filepath)
        }
        save_manifest(manifest)

def track_project_file(filepath, dry_run=False):
    manifest = load_manifest()
    if filepath not in manifest["project_files"]:
        if dry_run:
            print(f"[DRY-RUN] Would track project file: {filepath}")
            return
        manifest["project_files"].append(filepath)
        save_manifest(manifest)
