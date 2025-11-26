"""
Reproduction script to verify frontend imports.
Mimics the import logic in frontend/app.py
"""
import sys
import os
from pathlib import Path

# Add project root to path (simulating running from frontend/app.py)
# We are running this script from project root, so we need to adjust
# If this script is in project root:
sys.path.append(os.getcwd())

try:
    from backend.main import EmailProductivityBackend
    print("Successfully imported EmailProductivityBackend")
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Error: {e}")
