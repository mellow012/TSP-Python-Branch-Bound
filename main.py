"""
TSP Branch and Bound Solver
Main entry point for the application
Author: [Wisdom M Mlambia]
Date: October 20, 2025
"""

import sys
from src.gui import TSPApplication

def main():
    """Initialize and run the TSP application"""
    app = TSPApplication()
    app.run()

if __name__ == "__main__":
    main()