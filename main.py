#!/usr/bin/env python3
"""
Heimdall - Data Analytics Application

A modular, plugin-based data analytics application with clear separation of concerns.
"""
import sys
import os
import logging
import argparse
from pathlib import Path

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

# Try importing directly from the current directory
sys.path.insert(0, os.path.join(project_root, "heimdall"))

try:
    from PySide6 import QtCore, QtWidgets, QtGui
except ImportError:
    print("PySide6 is not installed. Please install it with pip: pip install pyside6")
    sys.exit(1)

try:
    from core.orchestrator import ApplicationOrchestrator
    from infrastructure.logging.logging_service import LoggingService
    from presentation.main.main_window import MainWindow
except ImportError as e:
    print(f"Error importing modules: {e}")
    print(f"Current Python path: {sys.path}")
    sys.exit(1)

def parse_args():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description="Heimdall - Data Analytics Application")
    parser.add_argument(
        "--config", 
        help="Path to configuration file"
    )
    parser.add_argument(
        "--headless", 
        action="store_true",
        help="Run in headless mode (no UI)"
    )
    parser.add_argument(
        "--log-level", 
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level"
    )
    
    return parser.parse_args()

def setup_logging(log_level="INFO"):
    """
    Set up basic logging configuration.
    """
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create logs directory in user's home directory
    log_dir = Path.home() / "Documents" / "Heimdall" / "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_dir / "heimdall.log")
        ]
    )

def run_ui(orchestrator):
    """
    Run the application with UI.
    """
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("Heimdall")
    app.setOrganizationName("Ben Sundem")
    
    # Apply stylesheet based on config
    theme = orchestrator.config_manager.get('ui', 'theme', 'light')
    if theme == 'dark':
        app.setStyle("Fusion")
        
        # Dark palette
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
        palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.Base, QtGui.QColor(25, 25, 25))
        palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
        palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
        palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
        palette.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))
        palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))
        palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
        app.setPalette(palette)
    
    main_window = MainWindow(orchestrator)
    main_window.show()
    
    return app.exec()

def run_headless(orchestrator):
    """
    Run the application in headless mode.
    """
    logger = logging.getLogger(__name__)
    logger.info("Running in headless mode")
    
    # In a real application, this would do something useful
    # For now, just print the available plugins
    for plugin_name, plugin in orchestrator.plugin_manager.plugins.items():
        logger.info(f"Found plugin: {plugin_name}")
    
    logger.info("Headless execution complete")
    return 0

def main():
    """
    Main application entry point.
    """
    # Parse command line arguments
    args = parse_args()
    
    # Set up logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    logger.info("Starting Heimdall application")
    
    try:
        # Initialize the application orchestrator
        orchestrator = ApplicationOrchestrator()
        
        # Initialize with configuration
        if args.config:
            config_path = args.config
        else:
            # Use default config in user's home directory
            config_dir = Path.home() / ".heimdall"
            os.makedirs(config_dir, exist_ok=True)
            config_path = config_dir / "config.json"
            if not config_path.exists():
                # First run, do not load config
                config_path = None
                logger.info("No configuration file found, using defaults")
                
        orchestrator.initialize(config_path)
        
        # Run the application in the appropriate mode
        if args.headless:
            return run_headless(orchestrator)
        else:
            return run_ui(orchestrator)
            
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        return 1
    finally:
        logger.info("Application exiting")

if __name__ == "__main__":
    sys.exit(main())