import time
import tracemalloc
import hashlib
import os
import generate
import backup_manager
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import rollback

def get_dir_hash(directory):
    """Return a combined hash of all files in a directory to verify determinism."""
    hashes = {}
    for root, _, files in os.walk(directory):
        for file in sorted(files):
            filepath = os.path.join(root, file)
            with open(filepath, "rb") as f:
                hashes[filepath] = hashlib.sha256(f.read()).hexdigest()
    return hashes

def main():
    print("=== Phase 3.5 Validation Pipeline ===")
    
    # 1. Performance Profiling
    print("\n[1] Performance & Memory Profiling")
    tracemalloc.start()
    start_time = time.time()
    
    generate.main()
    
    end_time = time.time()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    print(f"Total Pipeline Duration: {end_time - start_time:.2f} seconds")
    print(f"Peak Memory Usage: {peak / 10**6:.2f} MB")
    
    # 2. Determinism Check
    print("\n[2] Determinism Check")
    hashes_run_1 = get_dir_hash("preview")
    
    # Run again
    generate.main()
    hashes_run_2 = get_dir_hash("preview")
    
    deterministic = True
    for file, h1 in hashes_run_1.items():
        if h1 != hashes_run_2.get(file):
            print(f"  [FAIL] File {file} is not deterministic!")
            deterministic = False
    
    if deterministic:
        print("  [PASS] All generated files are byte-for-byte deterministic.")
        
    # 3. Rollback Validation
    print("\n[3] Rollback Validation")
    rollback.main()
    if not os.path.exists("preview"):
        print("  [PASS] Preview directory successfully removed.")
    else:
        print("  [FAIL] Preview directory still exists!")
        
    # 4. Regenerate after rollback
    print("\n[4] Post-Rollback Regeneration")
    generate.main()
    if os.path.exists("preview"):
        print("  [PASS] Successfully regenerated assets after rollback.")

if __name__ == "__main__":
    main()
