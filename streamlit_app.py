import sys
import os

# Ensure current directory is in Python path for module imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from ui.app import main

if __name__ == "__main__":
    main() 