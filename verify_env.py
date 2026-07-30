import os
import sys

def verify():
    print("Python version:", sys.version)
    print("Current working directory:", os.getcwd())
    
    required_dirs = [
        "assets", "components", "pages", "models", "training",
        "preprocessing", "utils", "config", "data", "explainability", "reports"
    ]
    
    missing_dirs = []
    for d in required_dirs:
        if not os.path.exists(d):
            missing_dirs.append(d)
            
    if missing_dirs:
        print("Missing directories:", missing_dirs)
    else:
        print("All required directories verified successfully.")
        
    modules = ["torch", "shap", "sklearn", "pandas", "numpy", "matplotlib"]
    print("Checking packages:")
    for mod in modules:
        try:
            __import__(mod)
            print(f"  - {mod}: OK")
        except ImportError:
            print(f"  - {mod}: MISSING")

if __name__ == "__main__":
    verify()
