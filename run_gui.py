"""
Main launcher for Composite Material Analysis GUI

Run this file to start the graphical user interface.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from composite_gui import main

if __name__ == "__main__":
    main()
