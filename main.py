# main.py
"""Application entry point"""

import sys
from PyQt6.QtWidgets import QApplication
from ui_manager import UIManager


def main():
    """Start the application"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = UIManager()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
