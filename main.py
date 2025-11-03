"""
TSP Branch and Bound Solver - PyQt5 Version
Main entry point for the application
Author: Wisdom M Mlambia
Date: October 2025
"""

import sys
from PyQt5.QtWidgets import QApplication
from src.gui_pyqt import TSPMainWindow


def main():
    """Initialize and run the TSP application"""
    # Create Qt application
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("TSP Branch & Bound Solver")
    app.setOrganizationName("University CS Department")
    
    # Create and show main window
    window = TSPMainWindow()
    window.show()
    
    # Run application event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()