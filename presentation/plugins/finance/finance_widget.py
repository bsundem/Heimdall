from typing import Dict, List, Any, Optional
import logging
from PySide6 import QtCore, QtWidgets, QtGui, QtWebEngineWidgets
import pandas as pd
import os
from pathlib import Path

from heimdall.core.orchestrator import ApplicationOrchestrator
from heimdall.plugins.finance.finance_plugin import FinancePlugin
from heimdall.presentation.ui_components import AsyncWidget, ExportDialog

class StockAnalysisTab(AsyncWidget):
    """
    Tab for stock price analysis.
    """
    def __init__(self, finance_plugin: FinancePlugin, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.finance_plugin = finance_plugin
        self.stock_data = None
        
        self._init_ui()
        
    def _init_ui(self):
        """
        Initialize the UI components.
        """
        layout = QtWidgets.QVBoxLayout()
        
        # Form for input parameters
        form_group = QtWidgets.QGroupBox("Stock Analysis Parameters")
        form_layout = QtWidgets.QFormLayout()
        
        # Ticker input
        self.ticker_edit = QtWidgets.QLineEdit("AAPL")
        form_layout.addRow("Ticker Symbol:", self.ticker_edit)
        
        # Days input
        self.days_spin = QtWidgets.QSpinBox()
        self.days_spin.setRange(10, 365)
        self.days_spin.setValue(90)
        self.days_spin.setSuffix(" days")
        form_layout.addRow("Historical Period:", self.days_spin)
        
        # Volatility input
        self.volatility_spin = QtWidgets.QDoubleSpinBox()
        self.volatility_spin.setRange(0.001, 0.1)
        self.volatility_spin.setValue(0.02)
        self.volatility_spin.setSingleStep(0.001)
        self.volatility_spin.setDecimals(3)
        form_layout.addRow("Volatility Factor:", self.volatility_spin)
        
        # Generate button
        self.generate_button = QtWidgets.QPushButton("Generate Analysis")
        self.generate_button.clicked.connect(self._generate_analysis)
        form_layout.addRow("", self.generate_button)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Results area
        results_layout = QtWidgets.QHBoxLayout()
        
        # Chart view
        self.chart_view = QtWebEngineWidgets.QWebEngineView()
        self.chart_view.setMinimumHeight(400)
        results_layout.addWidget(self.chart_view, 2)
        
        # Data view
        data_layout = QtWidgets.QVBoxLayout()
        self.data_table = QtWidgets.QTableView()
        self.data_table.setAlternatingRowColors(True)
        data_layout.addWidget(self.data_table)
        
        # Export button
        self.export_button = QtWidgets.QPushButton("Export Data as CSV")
        self.export_button.clicked.connect(self._export_data)
        self.export_button.setEnabled(False)
        data_layout.addWidget(self.export_button)
        
        results_layout.addLayout(data_layout, 1)
        
        layout.addLayout(results_layout)
        
        # Status label
        self.status_label = QtWidgets.QLabel("Ready")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
    def _generate_analysis(self):
        """
        Generate stock analysis based on input parameters.
        """
        ticker = self.ticker_edit.text().strip().upper()
        if not ticker:
            QtWidgets.QMessageBox.warning(
                self,
                "Input Error",
                "Please enter a valid ticker symbol."
            )
            return
            
        days = self.days_spin.value()
        volatility = self.volatility_spin.value()
        
        # Update status
        self.status_label.setText("Generating stock data...")
        self.generate_button.setEnabled(False)
        
        # Run in background
        self.run_async(
            self.finance_plugin.generate_sample_stock_data,
            ticker, days, 100.0, volatility,
            on_complete=self._on_data_generated,
            on_error=self._on_generate_error
        )
        
    def _on_data_generated(self, data):
        """
        Handle generated stock data.
        """
        self.stock_data = data
        
        # Display in table
        model = TableModel(data)
        self.data_table.setModel(model)
        
        # Update status
        self.status_label.setText("Generating chart...")
        
        # Generate chart
        self.run_async(
            self.finance_plugin.generate_stock_chart,
            data,
            on_complete=self._on_chart_generated,
            on_error=self._on_generate_error
        )
        
    def _on_chart_generated(self, result):
        """
        Handle generated chart.
        """
        if 'error' in result:
            self.status_label.setText(f"Error: {result['error']}")
            self.generate_button.setEnabled(True)
            return
            
        # Load chart image
        if 'plot_path' in result:
            plot_path = result['plot_path']
            html = f"""
            <html>
            <head>
                <style>
                    body {{ margin: 0; padding: 0; }}
                    img {{ max-width: 100%; height: auto; }}
                </style>
            </head>
            <body>
                <img src="file://{plot_path}" />
            </body>
            </html>
            """
            self.chart_view.setHtml(html)
            
        # Enable export
        self.export_button.setEnabled(True)
        
        # Update status
        self.status_label.setText("Analysis complete")
        self.generate_button.setEnabled(True)
        
    def _on_generate_error(self, error):
        """
        Handle generation error.
        """
        self.status_label.setText(f"Error: {error}")
        self.generate_button.setEnabled(True)
        
    def _export_data(self):
        """
        Export the stock data to CSV.
        """
        if self.stock_data is None:
            return
            
        ticker = self.ticker_edit.text().strip().upper()
        export_name = f"stock_analysis_{ticker}"
        
        dialog = ExportDialog(self.finance_plugin.export_service, self.stock_data, export_name, self)
        dialog.exec()


class PortfolioAnalysisTab(AsyncWidget):
    """
    Tab for portfolio allocation analysis.
    """
    def __init__(self, finance_plugin: FinancePlugin, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.finance_plugin = finance_plugin
        self.portfolio_data = None
        
        self._init_ui()
        
    def _init_ui(self):
        """
        Initialize the UI components.
        """
        layout = QtWidgets.QVBoxLayout()
        
        # Form for input parameters
        form_group = QtWidgets.QGroupBox("Portfolio Analysis Parameters")
        form_layout = QtWidgets.QFormLayout()
        
        # Tickers input
        ticker_layout = QtWidgets.QHBoxLayout()
        self.ticker_edit = QtWidgets.QLineEdit("AAPL, MSFT, GOOG, AMZN, TSLA")
        ticker_layout.addWidget(self.ticker_edit)
        form_layout.addRow("Ticker Symbols (comma-separated):", ticker_layout)
        
        # Portfolio value input
        self.value_spin = QtWidgets.QDoubleSpinBox()
        self.value_spin.setRange(1000, 10000000)
        self.value_spin.setValue(1000000)
        self.value_spin.setPrefix("$ ")
        self.value_spin.setSingleStep(1000)
        self.value_spin.setGroupSeparatorShown(True)
        form_layout.addRow("Portfolio Value:", self.value_spin)
        
        # Generate button
        self.generate_button = QtWidgets.QPushButton("Generate Portfolio Analysis")
        self.generate_button.clicked.connect(self._generate_analysis)
        form_layout.addRow("", self.generate_button)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Results area
        results_layout = QtWidgets.QHBoxLayout()
        
        # Chart view
        self.chart_view = QtWebEngineWidgets.QWebEngineView()
        self.chart_view.setMinimumHeight(400)
        results_layout.addWidget(self.chart_view, 2)
        
        # Data view
        data_layout = QtWidgets.QVBoxLayout()
        self.data_table = QtWidgets.QTableView()
        self.data_table.setAlternatingRowColors(True)
        data_layout.addWidget(self.data_table)
        
        # Export button
        self.export_button = QtWidgets.QPushButton("Export Data as CSV")
        self.export_button.clicked.connect(self._export_data)
        self.export_button.setEnabled(False)
        data_layout.addWidget(self.export_button)
        
        results_layout.addLayout(data_layout, 1)
        
        layout.addLayout(results_layout)
        
        # Status label
        self.status_label = QtWidgets.QLabel("Ready")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
    def _generate_analysis(self):
        """
        Generate portfolio analysis based on input parameters.
        """
        tickers_text = self.ticker_edit.text().strip()
        if not tickers_text:
            QtWidgets.QMessageBox.warning(
                self,
                "Input Error",
                "Please enter at least one ticker symbol."
            )
            return
            
        # Parse tickers
        tickers = [t.strip().upper() for t in tickers_text.split(',')]
        tickers = [t for t in tickers if t]  # Remove empty strings
        
        if not tickers:
            QtWidgets.QMessageBox.warning(
                self,
                "Input Error",
                "Please enter valid ticker symbols."
            )
            return
            
        portfolio_value = self.value_spin.value()
        
        # Update status
        self.status_label.setText("Generating portfolio data...")
        self.generate_button.setEnabled(False)
        
        # Run in background
        self.run_async(
            self.finance_plugin.generate_sample_portfolio,
            tickers, portfolio_value,
            on_complete=self._on_data_generated,
            on_error=self._on_generate_error
        )
        
    def _on_data_generated(self, data):
        """
        Handle generated portfolio data.
        """
        self.portfolio_data = data
        
        # Display in table
        model = TableModel(data)
        self.data_table.setModel(model)
        
        # Update status
        self.status_label.setText("Generating chart...")
        
        # Generate chart
        self.run_async(
            self.finance_plugin.generate_portfolio_chart,
            data,
            on_complete=self._on_chart_generated,
            on_error=self._on_generate_error
        )
        
    def _on_chart_generated(self, result):
        """
        Handle generated chart.
        """
        if 'error' in result:
            self.status_label.setText(f"Error: {result['error']}")
            self.generate_button.setEnabled(True)
            return
            
        # Load chart image
        if 'plot_path' in result:
            plot_path = result['plot_path']
            html = f"""
            <html>
            <head>
                <style>
                    body {{ margin: 0; padding: 0; }}
                    img {{ max-width: 100%; height: auto; }}
                </style>
            </head>
            <body>
                <img src="file://{plot_path}" />
            </body>
            </html>
            """
            self.chart_view.setHtml(html)
            
        # Enable export
        self.export_button.setEnabled(True)
        
        # Update status
        self.status_label.setText("Analysis complete")
        self.generate_button.setEnabled(True)
        
    def _on_generate_error(self, error):
        """
        Handle generation error.
        """
        self.status_label.setText(f"Error: {error}")
        self.generate_button.setEnabled(True)
        
    def _export_data(self):
        """
        Export the portfolio data to CSV.
        """
        if self.portfolio_data is None:
            return
            
        export_name = "portfolio_analysis"
        
        dialog = ExportDialog(self.finance_plugin.export_service, self.portfolio_data, export_name, self)
        dialog.exec()


class FinanceWidget(QtWidgets.QWidget):
    """
    Widget for the finance domain.
    """
    def __init__(self, finance_plugin: FinancePlugin, orchestrator: ApplicationOrchestrator, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.finance_plugin = finance_plugin
        self.orchestrator = orchestrator
        
        self._init_ui()
        
    def _init_ui(self):
        """
        Initialize the UI components.
        """
        layout = QtWidgets.QVBoxLayout()
        
        # Create tab widget
        self.tab_widget = QtWidgets.QTabWidget()
        
        # Stock analysis tab
        self.stock_tab = StockAnalysisTab(self.finance_plugin)
        self.tab_widget.addTab(self.stock_tab, "Stock Analysis")
        
        # Portfolio analysis tab
        self.portfolio_tab = PortfolioAnalysisTab(self.finance_plugin)
        self.tab_widget.addTab(self.portfolio_tab, "Portfolio Allocation")
        
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)


class TableModel(QtCore.QAbstractTableModel):
    """
    Model for displaying pandas DataFrames in QTableViews.
    """
    def __init__(self, data: pd.DataFrame):
        super().__init__()
        self._data = data
        
    def rowCount(self, parent=None):
        return len(self._data)
        
    def columnCount(self, parent=None):
        return len(self._data.columns)
        
    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None
            
        if role == QtCore.Qt.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            
            # Format value based on type
            if isinstance(value, float):
                if value < 0.001 and value > 0:
                    return f"{value:.6f}"
                else:
                    return f"{value:.2f}"
            elif pd.isna(value):
                return ""
            else:
                return str(value)
                
        return None
        
    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return str(self._data.columns[section])
            
        if orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
            return str(self._data.index[section])
            
        return None