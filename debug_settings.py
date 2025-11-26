import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

try:
    from backend.config.settings import settings
    print("Settings loaded successfully")
except Exception as e:
    print(f"Error loading settings: {e}")
