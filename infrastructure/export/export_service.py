from typing import Dict, List, Any, Optional, Union, Callable
import logging
import pandas as pd
import os
import csv
from pathlib import Path
from datetime import datetime

class ExportService:
    """
    Central service managing data exports across the application.
    """
    def __init__(self, config_manager=None):
        self.logger = logging.getLogger(__name__)
        self.config_manager = config_manager
        self.exporters = {}
        self.register_default_exporters()
        
    def register_default_exporters(self) -> None:
        """
        Register default exporters for common formats.
        """
        self.register_exporter("csv", self.export_csv)
        
    def register_exporter(self, format_name: str, exporter_func: Callable) -> None:
        """
        Register an exporter for a specific format.
        
        Args:
            format_name: The name of the format (e.g., 'csv', 'excel')
            exporter_func: A function that takes (data, filename, **options) and exports the data
        """
        self.exporters[format_name.lower()] = exporter_func
        self.logger.debug(f"Registered exporter for format: {format_name}")
        
    def export_data(self, data: Any, file_path: str, format_type: Optional[str] = None, **options) -> Dict[str, Any]:
        """
        Export data to a file.
        
        Args:
            data: The data to export (usually a pandas DataFrame)
            file_path: The path to export to
            format_type: The format to export as (defaults to file extension or 'csv')
            **options: Additional options to pass to the exporter
            
        Returns:
            A dictionary with the result of the export operation
        """
        try:
            # Determine format from file extension if not provided
            if not format_type:
                file_ext = os.path.splitext(file_path)[1].lower().lstrip('.')
                format_type = file_ext if file_ext else 'csv'
                
            format_type = format_type.lower()
            
            # Check if format is supported
            if format_type not in self.exporters:
                return {"success": False, "error": f"Unsupported export format: {format_type}"}
                
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            # Call the appropriate exporter
            exporter = self.exporters[format_type]
            exporter(data, file_path, **options)
            
            return {
                "success": True,
                "file_path": file_path,
                "format": format_type
            }
            
        except Exception as e:
            self.logger.error(f"Error exporting data: {e}")
            return {
                "success": False,
                "error": str(e)
            }
            
    def export_csv(self, data: Any, file_path: str, **options) -> None:
        """
        Export data to a CSV file.
        
        Args:
            data: The data to export (usually a pandas DataFrame)
            file_path: The path to export to
            **options: Additional options including:
                - delimiter: The CSV delimiter (default: ',')
                - quotechar: The quote character (default: '"')
                - encoding: File encoding (default: 'utf-8')
                - include_header: Whether to include the header (default: True)
                - date_format: Format for date columns (default: '%Y-%m-%d')
        """
        # Set default options
        delimiter = options.get('delimiter', ',')
        quotechar = options.get('quotechar', '"')
        encoding = options.get('encoding', 'utf-8')
        include_header = options.get('include_header', True)
        date_format = options.get('date_format', '%Y-%m-%d')
        
        if isinstance(data, pd.DataFrame):
            data.to_csv(
                file_path,
                sep=delimiter,
                quotechar=quotechar,
                encoding=encoding,
                index=options.get('include_index', False),
                header=include_header,
                date_format=date_format
            )
        else:
            # For non-DataFrame data, try to convert to CSV manually
            with open(file_path, 'w', newline='', encoding=encoding) as csvfile:
                writer = csv.writer(
                    csvfile, 
                    delimiter=delimiter,
                    quotechar=quotechar,
                    quoting=csv.QUOTE_MINIMAL
                )
                
                # Write rows depending on data type
                if isinstance(data, list):
                    if all(isinstance(item, dict) for item in data):
                        # List of dictionaries
                        if data and include_header:
                            writer.writerow(data[0].keys())
                        for item in data:
                            writer.writerow(item.values())
                    else:
                        # List of lists or values
                        for item in data:
                            if isinstance(item, (list, tuple)):
                                writer.writerow(item)
                            else:
                                writer.writerow([item])
                elif isinstance(data, dict):
                    # Dictionary
                    if include_header:
                        writer.writerow(['Key', 'Value'])
                    for key, value in data.items():
                        writer.writerow([key, value])
                else:
                    # Single value
                    writer.writerow([data])
                    
    def get_default_export_path(self, base_name: str, format_type: str = 'csv') -> str:
        """
        Get a default export path based on configuration.
        
        Args:
            base_name: The base name for the exported file
            format_type: The file format extension
            
        Returns:
            A complete file path for the export
        """
        if self.config_manager:
            default_path = self.config_manager.get('export', 'default_path', str(Path.home() / "Documents" / "Heimdall" / "exports"))
        else:
            default_path = str(Path.home() / "Documents" / "Heimdall" / "exports")
            
        # Ensure directory exists
        os.makedirs(default_path, exist_ok=True)
        
        # Add timestamp to filename for uniqueness
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{base_name}_{timestamp}.{format_type}"
        
        return os.path.join(default_path, filename)