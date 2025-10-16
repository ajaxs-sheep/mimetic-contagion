#!/usr/bin/env python3
"""
Entry point for mimetic contagion simulator.

Usage: python run.py [arguments]

Examples:
  python run.py --nodes Alice Betty Charlie David \\
                --initial all-positive \\
                --perturb Alice:Betty \\
                --seed 42

  python run.py --help
"""

import sys
from src.cli import main

if __name__ == "__main__":
    main()
