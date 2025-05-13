from typing import Dict, List, Any, Optional
import logging
from PySide6 import QtCore, QtWidgets, QtGui
import os
from pathlib import Path

from heimdall.core.orchestrator import ApplicationOrchestrator

class SettingsDialog(QtWidgets.QDialog):
    """
    Dialog for configuring application settings.
    """
    def __init__(self, orchestrator: ApplicationOrchestrator, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.orchestrator = orchestrator
        self.config_manager = orchestrator.config_manager
        
        self._init_ui()
        self._load_settings()
        
    def _init_ui(self):
        """
        Initialize the UI components.
        """
        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)
        
        layout = QtWidgets.QVBoxLayout()
        
        # Create tab widget
        self.tab_widget = QtWidgets.QTabWidget()
        
        # General tab
        general_tab = QtWidgets.QWidget()
        general_layout = QtWidgets.QFormLayout()
        
        # Theme selection
        self.theme_combo = QtWidgets.QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        general_layout.addRow("Theme:", self.theme_combo)
        
        # Log level selection
        self.log_level_combo = QtWidgets.QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        general_layout.addRow("Logging Level:", self.log_level_combo)
        
        general_tab.setLayout(general_layout)
        self.tab_widget.addTab(general_tab, "General")
        
        # Export tab
        export_tab = QtWidgets.QWidget()
        export_layout = QtWidgets.QFormLayout()
        
        # Default format
        self.default_format_combo = QtWidgets.QComboBox()
        self.default_format_combo.addItems(["CSV", "Excel", "JSON"])
        export_layout.addRow("Default Format:", self.default_format_combo)
        
        # Default export path
        path_layout = QtWidgets.QHBoxLayout()
        self.export_path_edit = QtWidgets.QLineEdit()
        path_layout.addWidget(self.export_path_edit)
        
        browse_button = QtWidgets.QPushButton("Browse...")
        browse_button.clicked.connect(self._browse_export_path)
        path_layout.addWidget(browse_button)
        
        export_layout.addRow("Default Export Path:", path_layout)
        
        export_tab.setLayout(export_layout)
        self.tab_widget.addTab(export_tab, "Export")
        
        # R Integration tab
        r_tab = QtWidgets.QWidget()
        r_layout = QtWidgets.QFormLayout()
        
        # Enable R integration
        self.r_enabled_check = QtWidgets.QCheckBox()
        r_layout.addRow("Enable R Integration:", self.r_enabled_check)
        
        # R timeout
        self.r_timeout_spin = QtWidgets.QSpinBox()
        self.r_timeout_spin.setRange(1, 300)
        self.r_timeout_spin.setSuffix(" seconds")
        r_layout.addRow("R Script Timeout:", self.r_timeout_spin)
        
        r_tab.setLayout(r_layout)
        self.tab_widget.addTab(r_tab, "R Integration")
        
        layout.addWidget(self.tab_widget)
        
        # Buttons
        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self._save_settings)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
    def _load_settings(self):
        """
        Load current settings into the UI.
        """
        # General tab
        theme = self.config_manager.get('ui', 'theme', 'light')
        self.theme_combo.setCurrentText(theme.capitalize())
        
        log_level = self.config_manager.get('app', 'logging_level', 'INFO')
        self.log_level_combo.setCurrentText(log_level)
        
        # Export tab
        default_format = self.config_manager.get('export', 'default_format', 'csv')
        self.default_format_combo.setCurrentText(default_format.upper())
        
        export_path = self.config_manager.get('export', 'default_path',
                                             str(Path.home() / "Documents" / "Heimdall" / "exports"))
        self.export_path_edit.setText(export_path)
        
        # R Integration tab
        r_enabled = self.config_manager.get('r_integration', 'enabled', True)
        self.r_enabled_check.setChecked(r_enabled)
        
        r_timeout = self.config_manager.get('r_integration', 'timeout', 30)
        self.r_timeout_spin.setValue(r_timeout)
        
    def _save_settings(self):
        """
        Save settings from the UI.
        """
        # General tab
        theme = self.theme_combo.currentText().lower()
        self.config_manager.set('ui', 'theme', theme)
        
        log_level = self.log_level_combo.currentText()
        self.config_manager.set('app', 'logging_level', log_level)
        
        # Export tab
        default_format = self.default_format_combo.currentText().lower()
        self.config_manager.set('export', 'default_format', default_format)
        
        export_path = self.export_path_edit.text()
        self.config_manager.set('export', 'default_path', export_path)
        
        # R Integration tab
        r_enabled = self.r_enabled_check.isChecked()
        self.config_manager.set('r_integration', 'enabled', r_enabled)
        
        r_timeout = self.r_timeout_spin.value()
        self.config_manager.set('r_integration', 'timeout', r_timeout)
        
        # Save to config file
        config_dir = Path.home() / ".heimdall"
        os.makedirs(config_dir, exist_ok=True)
        config_file = config_dir / "config.json"
        
        try:
            self.config_manager.save_to_file(str(config_file))
            self.logger.info(f"Settings saved to {config_file}")
        except Exception as e:
            self.logger.error(f"Error saving settings: {e}")
            QtWidgets.QMessageBox.warning(
                self,
                "Settings Error",
                f"Failed to save settings: {str(e)}"
            )
            
        self.accept()
        
    def _browse_export_path(self):
        """
        Show a directory dialog to browse for export path.
        """
        current_path = self.export_path_edit.text()
        directory = current_path if current_path else str(Path.home())
        
        new_path = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Select Export Directory",
            directory,
            QtWidgets.QFileDialog.ShowDirsOnly
        )
        
        if new_path:
            self.export_path_edit.setText(new_path)