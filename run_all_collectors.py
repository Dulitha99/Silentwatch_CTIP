import subprocess
import os
import sys

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    collectors_dir = os.path.join(base_dir, "collectors")
    
    # List of collector scripts to run
    collectors = [
        "malwarebazaar.py",
        "urlhaus.py",
        "otx.py",
        "cisa_kev.py",
        "nvd.py"
    ]
    
    for collector in collectors:
        script_path = os.path.join(collectors_dir, collector)
        if os.path.exists(script_path):
            print(f"[{collector}] Starting collector...")
            try:
                result = subprocess.run([sys.executable, script_path], check=True)
                print(f"[{collector}] Completed successfully.\n")
            except subprocess.CalledProcessError as e:
                print(f"[{collector}] Failed with error: {e}\n")
        else:
            print(f"[{collector}] Script not found at {script_path}\n")

if __name__ == "__main__":
    main()
