#!/usr/bin/env python3
"""
Simple PySide6 application to test GUI functionality.
"""
import sys
from PySide6 import QtWidgets, QtCore

class SimpleWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Heimdall - Simple Test")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QtWidgets.QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Add title
        title = QtWidgets.QLabel("Heimdall")
        title_font = title.font()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)
        
        # Add subtitle
        subtitle = QtWidgets.QLabel("A Great Bridge Shall Open The Way")
        subtitle_font = subtitle.font()
        subtitle_font.setPointSize(16)
        subtitle.setFont(subtitle_font)
        subtitle.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        # Add button
        button = QtWidgets.QPushButton("Click Me")
        button.clicked.connect(self.button_clicked)
        layout.addWidget(button)
        
        # Add status bar
        self.status_bar = QtWidgets.QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
    def button_clicked(self):
        """Handle button click."""
        self.status_bar.showMessage("Button clicked!")
        QtWidgets.QMessageBox.information(self, "Message", "Hello from Heimdall!")

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = SimpleWindow()
    window.show()
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())