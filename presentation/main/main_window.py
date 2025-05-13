from typing import Dict, List, Any, Optional
import logging
import sys
from pathlib import Path
from PySide6 import QtCore, QtWidgets, QtGui

from heimdall.core.orchestrator import ApplicationOrchestrator
from heimdall.presentation.settings.settings_dialog import SettingsDialog
from heimdall.presentation.ui_components import AsyncWidget

class MainWindow(QtWidgets.QMainWindow):
    """
    Main application window.
    """
    def __init__(self, orchestrator: ApplicationOrchestrator):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.orchestrator = orchestrator
        
        self._init_ui()
        
    def _init_ui(self):
        """
        Initialize the UI components.
        """
        # Set window properties
        self.setWindowTitle("Heimdall - Data Analytics")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create the central tab widget
        self.tab_widget = QtWidgets.QTabWidget()
        self.setCentralWidget(self.tab_widget)
        
        # Create tabs
        self._create_home_tab()
        self._create_domain_tabs()
        
        # Create menu
        self._create_menu()
        
        # Create status bar
        self.status_bar = QtWidgets.QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
    def _create_menu(self):
        """
        Create the application menu.
        """
        # Main menu bar
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("&File")
        
        # Settings action
        settings_action = QtGui.QAction("&Settings", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self._show_settings)
        file_menu.addAction(settings_action)
        
        # Exit action
        exit_action = QtGui.QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menu_bar.addMenu("&Help")
        
        # About action
        about_action = QtGui.QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
        
    def _create_home_tab(self):
        """
        Create the home tab.
        """
        home_tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        
        # Title
        title_label = QtWidgets.QLabel("Welcome to Heimdall")
        title_font = title_label.font()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QtWidgets.QLabel("A Great Bridge Shall Open The Way")
        subtitle_font = subtitle_label.font()
        subtitle_font.setPointSize(16)
        subtitle_font.setItalic(True)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(subtitle_label)
        
        # Spacer
        layout.addSpacing(20)
        
        # Description
        description = """
        <p style='font-size: 14px; text-align: center;'>
        Heimdall is a modular, plugin-based data analytics application with clear separation of concerns.
        The design aligns with SOLID principles and enables both UI-based and headless operation modes.
        </p>
        <p style='font-size: 14px; text-align: center;'>
        Use the tabs above to navigate to different analysis domains.
        </p>
        """
        desc_label = QtWidgets.QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(desc_label)
        
        # Spacer
        layout.addSpacing(40)
        
        # Quick start section
        quick_start_group = QtWidgets.QGroupBox("Quick Start")
        quick_start_layout = QtWidgets.QVBoxLayout()
        
        # Create buttons for each plugin
        for plugin_name, plugin in self.orchestrator.plugin_manager.plugins.items():
            button = QtWidgets.QPushButton(f"Open {plugin_name.capitalize()} Domain")
            # Use a lambda with default argument to avoid late binding issues
            button.clicked.connect(lambda checked, name=plugin_name: self._switch_to_tab(name))
            quick_start_layout.addWidget(button)
        
        quick_start_group.setLayout(quick_start_layout)
        layout.addWidget(quick_start_group)
        
        # Add stretch to push everything to the top
        layout.addStretch()
        
        home_tab.setLayout(layout)
        self.tab_widget.addTab(home_tab, "Home")
        
    def _create_domain_tabs(self):
        """
        Create tabs for each domain plugin.
        """
        # Dynamically create tabs for each plugin
        for plugin_name, plugin in self.orchestrator.plugin_manager.plugins.items():
            # Import the appropriate UI module based on plugin name
            try:
                if plugin_name == "finance":
                    from heimdall.presentation.plugins.finance.finance_widget import FinanceWidget
                    tab = FinanceWidget(plugin, self.orchestrator)
                    self.tab_widget.addTab(tab, "Finance")
                else:
                    # Generic tab for unrecognized plugins
                    tab = QtWidgets.QWidget()
                    layout = QtWidgets.QVBoxLayout()
                    label = QtWidgets.QLabel(f"Plugin: {plugin_name}")
                    layout.addWidget(label)
                    tab.setLayout(layout)
                    self.tab_widget.addTab(tab, plugin_name.capitalize())
            except Exception as e:
                self.logger.error(f"Error creating tab for plugin {plugin_name}: {e}")
                
    def _switch_to_tab(self, tab_name: str):
        """
        Switch to a specific tab by name.
        """
        # Find the tab index by name
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i).lower() == tab_name.lower():
                self.tab_widget.setCurrentIndex(i)
                return
                
    def _show_settings(self):
        """
        Show the settings dialog.
        """
        dialog = SettingsDialog(self.orchestrator, self)
        dialog.exec()
        
    def _show_about(self):
        """
        Show the about dialog.
        """
        QtWidgets.QMessageBox.about(
            self,
            "About Heimdall",
            "<h3>Heimdall</h3>"
            "<p>A Great Bridge Shall Open The Way</p>"
            "<p>Version 0.1.0</p>"
            "<p>A modular, plugin-based data analytics application.</p>"
            "<p>© 2025 Ben Sundem</p>"
        )
        
    def closeEvent(self, event: QtGui.QCloseEvent):
        """
        Handle window close event.
        """
        # Clean shutdown of the application
        self.orchestrator.shutdown()
        event.accept()