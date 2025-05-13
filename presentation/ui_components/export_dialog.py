from typing import Dict, List, Any, Optional, Callable
import logging
from PySide6 import QtCore, QtWidgets
import os
from pathlib import Path

class ExportDialog(QtWidgets.QDialog):
    """
    Dialog for configuring and executing exports.
    """
    def __init__(self, export_service, data, name, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.export_service = export_service
        self.data = data
        self.name = name
        
        self.result = None
        
        self._init_ui()
        
    def _init_ui(self):
        """
        Initialize the UI components.
        """
        self.setWindowTitle("Export Data")
        self.setMinimumWidth(500)
        
        layout = QtWidgets.QVBoxLayout()
        
        # File path
        path_layout = QtWidgets.QHBoxLayout()
        path_layout.addWidget(QtWidgets.QLabel("File:"))
        
        self.path_edit = QtWidgets.QLineEdit()
        default_path = self.export_service.get_default_export_path(self.name)
        self.path_edit.setText(default_path)
        path_layout.addWidget(self.path_edit)
        
        browse_button = QtWidgets.QPushButton("Browse...")
        browse_button.clicked.connect(self._browse_path)
        path_layout.addWidget(browse_button)
        
        layout.addLayout(path_layout)
        
        # Format options
        format_group = QtWidgets.QGroupBox("Format Options")
        format_layout = QtWidgets.QVBoxLayout()
        
        # Delimiter
        delimiter_layout = QtWidgets.QHBoxLayout()
        delimiter_layout.addWidget(QtWidgets.QLabel("Delimiter:"))
        self.delimiter_combo = QtWidgets.QComboBox()
        self.delimiter_combo.addItems([
            "Comma (,)",
            "Tab (\\t)",
            "Semicolon (;)",
            "Pipe (|)"
        ])
        delimiter_layout.addWidget(self.delimiter_combo)
        format_layout.addLayout(delimiter_layout)
        
        # Encoding
        encoding_layout = QtWidgets.QHBoxLayout()
        encoding_layout.addWidget(QtWidgets.QLabel("Encoding:"))
        self.encoding_combo = QtWidgets.QComboBox()
        self.encoding_combo.addItems([
            "UTF-8",
            "latin-1",
            "ascii",
            "UTF-16"
        ])
        encoding_layout.addWidget(self.encoding_combo)
        format_layout.addLayout(encoding_layout)
        
        # Include header
        self.header_check = QtWidgets.QCheckBox("Include header row")
        self.header_check.setChecked(True)
        format_layout.addWidget(self.header_check)
        
        # Include index
        self.index_check = QtWidgets.QCheckBox("Include index column")
        self.index_check.setChecked(False)
        format_layout.addWidget(self.index_check)
        
        format_group.setLayout(format_layout)
        layout.addWidget(format_group)
        
        # Buttons
        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self._export)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
    def _browse_path(self):
        """
        Show a file dialog to browse for export path.
        """
        current_path = self.path_edit.text()
        directory = os.path.dirname(current_path) if current_path else str(Path.home())
        
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Export File",
            directory,
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if file_path:
            self.path_edit.setText(file_path)
            
    def _export(self):
        """
        Export the data with the selected options.
        """
        file_path = self.path_edit.text()
        if not file_path:
            QtWidgets.QMessageBox.warning(self, "Export Error", "Please specify a file path.")
            return
            
        # Get delimiter
        delimiter_map = {
            0: ',',    # Comma
            1: '\t',   # Tab
            2: ';',    # Semicolon
            3: '|'     # Pipe
        }
        delimiter = delimiter_map.get(self.delimiter_combo.currentIndex(), ',')
        
        # Get encoding
        encoding = self.encoding_combo.currentText().lower()
        
        # Get other options
        include_header = self.header_check.isChecked()
        include_index = self.index_check.isChecked()
        
        # Export the data
        try:
            result = self.export_service.export_data(
                self.data,
                file_path,
                format_type='csv',
                delimiter=delimiter,
                encoding=encoding,
                include_header=include_header,
                include_index=include_index
            )
            
            if result['success']:
                QtWidgets.QMessageBox.information(
                    self,
                    "Export Successful",
                    f"Data exported to {result['file_path']}"
                )
                self.result = result
                self.accept()
            else:
                QtWidgets.QMessageBox.critical(
                    self,
                    "Export Error",
                    f"Failed to export data: {result.get('error', 'Unknown error')}"
                )
        except Exception as e:
            self.logger.error(f"Export error: {e}")
            QtWidgets.QMessageBox.critical(
                self,
                "Export Error",
                f"An error occurred during export: {str(e)}"
            )