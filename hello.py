#!/usr/bin/env python3
"""
Simple test script to verify Python environment.
"""
import sys
import os

def main():
    print(f"Hello from Python {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Python executable: {sys.executable}")
    print(f"Python path: {sys.path}")
    
    # Check for required modules
    try:
        import PySide6
        print(f"PySide6 installed: {PySide6.__version__}")
    except ImportError:
        print("PySide6 not installed")
    
    try:
        import pandas
        print(f"pandas installed: {pandas.__version__}")
    except ImportError:
        print("pandas not installed")
    
    try:
        import numpy
        print(f"numpy installed: {numpy.__version__}")
    except ImportError:
        print("numpy not installed")

if __name__ == "__main__":
    main()