import os
import shutil
import json
import sys

BACKUP_DIR = ".backup"
MANIFEST_FILE = os.path.join(BACKUP_DIR, "manifest.json")

def remove_path(path):
    if not os.path.exists(path):
        return
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
        print(f"Removed: {path}")
    except Exception as e:
        print(f"Failed to remove {path}: {e}")

def rollback():
    print("Starting complete rollback and recovery...")

    if not os.path.exists(MANIFEST_FILE):
        print("No backup manifest found. The repository appears to be clean.")
    else:
        with open(MANIFEST_FILE, "r") as f:
            manifest = json.load(f)

        # 1. Delete generated files (e.g. SVGs, workflow files)
        for filepath in manifest.get("generated_files", {}):
            remove_path(filepath)

        # 2. Restore backups (e.g. README.md)
        for original_file, backup_info in manifest.get("backups", {}).items():
            backup_path = backup_info.get("backup_path")
            if backup_path and os.path.exists(backup_path):
                # Ensure the parent directory exists if it was deleted
                parent_dir = os.path.dirname(original_file)
                if parent_dir and not os.path.exists(parent_dir):
                    os.makedirs(parent_dir)
                shutil.copy2(backup_path, original_file)
                print(f"Restored original state of: {original_file}")

        # 3. Delete tracked project files (scripts, configs)
        for filepath in manifest.get("project_files", []):
            if filepath != __file__: # Don't delete ourselves just yet
                remove_path(filepath)

    # 4. Remove standard project directories
    print("Cleaning up project directories...")
    remove_path("venv")
    remove_path("assets")
    remove_path("scripts")
    remove_path("preview")
    # Clean up workflow folder if it's empty after our workflow is removed
    if os.path.exists(".github/workflows") and not os.listdir(".github/workflows"):
        remove_path(".github/workflows")
    
    # 5. Remove the backup directory itself
    remove_path(BACKUP_DIR)
    
    print("Rollback complete. The repository has been restored.")
    
    # Finally, try to delete this script itself
    try:
        if os.path.exists(__file__):
            os.remove(__file__)
            print("Removed rollback.py")
    except Exception:
        pass

if __name__ == "__main__":
    # Change to the directory where rollback.py is located
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    rollback()
