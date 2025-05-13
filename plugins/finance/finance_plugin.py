from typing import Dict, List, Any, Optional
import logging
from heimdall.core.plugin_manager import PluginInterface
from heimdall.core.event_bus import EventBus, Event
from heimdall.infrastructure.r_integration.r_executor import RExecutor
from heimdall.infrastructure.export.export_service import ExportService
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class FinancePlugin(PluginInterface):
    """
    Plugin for finance domain functionality.
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.r_executor = None
        self.export_service = None
        
    @property
    def name(self) -> str:
        return "finance"
        
    def initialize(self) -> None:
        """
        Initialize the finance plugin.
        """
        self.logger.info("Initializing finance plugin")
        
        # Initialize R executor for this plugin
        self.r_executor = RExecutor()
        self.r_executor.initialize()
        
        # Initialize export service
        self.export_service = ExportService()
        
    def shutdown(self) -> None:
        """
        Shutdown the finance plugin.
        """
        self.logger.info("Shutting down finance plugin")
        if self.r_executor:
            self.r_executor.shutdown()
            
    def generate_sample_stock_data(self, ticker: str, days: int = 90, 
                                 start_price: float = 100.0, volatility: float = 0.02) -> pd.DataFrame:
        """
        Generate sample stock price data for demonstration purposes.
        
        Args:
            ticker: The stock ticker symbol
            days: Number of days of data to generate
            start_price: Starting price for the stock
            volatility: Daily price volatility factor
            
        Returns:
            DataFrame with date, open, high, low, close, volume
        """
        np.random.seed(42)  # For reproducibility
        
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        dates = [start_date + timedelta(days=i) for i in range(days)]
        dates = [d for d in dates if d.weekday() < 5]  # Only business days
        
        # Generate price data with random walk
        price = start_price
        opens = []
        highs = []
        lows = []
        closes = []
        volumes = []
        
        for _ in dates:
            change_percent = np.random.normal(0, volatility)
            price = price * (1 + change_percent)
            
            # Generate OHLC data
            open_price = price * (1 + np.random.normal(0, volatility/2))
            close_price = price * (1 + np.random.normal(0, volatility/2))
            high_price = max(open_price, close_price) * (1 + abs(np.random.normal(0, volatility)))
            low_price = min(open_price, close_price) * (1 - abs(np.random.normal(0, volatility)))
            
            # Generate volume
            volume = int(np.random.normal(1000000, 200000))
            
            opens.append(open_price)
            closes.append(close_price)
            highs.append(high_price)
            lows.append(low_price)
            volumes.append(volume)
            
        # Create DataFrame
        df = pd.DataFrame({
            'date': dates,
            'ticker': ticker,
            'open': opens,
            'high': highs,
            'low': lows,
            'close': closes,
            'volume': volumes
        })
        
        return df
        
    def generate_sample_portfolio(self, tickers: List[str], 
                               total_value: float = 1000000.0) -> pd.DataFrame:
        """
        Generate a sample portfolio allocation for demonstration purposes.
        
        Args:
            tickers: List of ticker symbols
            total_value: Total portfolio value
            
        Returns:
            DataFrame with portfolio allocation
        """
        # Generate random weights that sum to 1
        weights = np.random.dirichlet(np.ones(len(tickers)))
        
        # Generate random prices
        prices = np.random.uniform(10, 500, len(tickers))
        
        # Calculate shares and values
        values = weights * total_value
        shares = values / prices
        
        # Create DataFrame
        df = pd.DataFrame({
            'ticker': tickers,
            'price': prices,
            'shares': shares,
            'value': values,
            'weight': weights,
            'allocation': [f"{w:.1%}" for w in weights]
        })
        
        # Sort by value (descending)
        df = df.sort_values('value', ascending=False).reset_index(drop=True)
        
        return df
        
    def generate_stock_chart(self, stock_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate a stock price chart using R.
        
        Args:
            stock_data: DataFrame with stock price data
            
        Returns:
            Dictionary with chart results
        """
        if not self.r_executor:
            return {"error": "R executor not initialized"}
            
        # Define R script for generating a stock chart
        r_script = """
        # Load required libraries
        if (!require(ggplot2)) install.packages("ggplot2", repos="https://cloud.r-project.org")
        library(ggplot2)
        
        # Create plot
        p <- ggplot(stock_data, aes(x=date, y=close)) +
          geom_line(color="steelblue") +
          geom_ribbon(aes(ymin=low, ymax=high), alpha=0.2, fill="steelblue") +
          labs(title=paste("Stock Price:", unique(stock_data$ticker)),
               x="Date", y="Price") +
          theme_minimal()
          
        # Save the plot
        plot_file <- tempfile(fileext=".png")
        ggsave(plot_file, p, width=10, height=6)
        
        # Create results object
        results <- list(plot_path=plot_file)
        """
        
        # Execute R script
        return self.r_executor.execute_script(r_script, {"stock_data": stock_data})
        
    def generate_portfolio_chart(self, portfolio_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate a portfolio allocation chart using R.
        
        Args:
            portfolio_data: DataFrame with portfolio allocation data
            
        Returns:
            Dictionary with chart results
        """
        if not self.r_executor:
            return {"error": "R executor not initialized"}
            
        # Define R script for generating a portfolio chart
        r_script = """
        # Load required libraries
        if (!require(ggplot2)) install.packages("ggplot2", repos="https://cloud.r-project.org")
        library(ggplot2)
        
        # Create plot
        p <- ggplot(portfolio_data, aes(x="", y=weight, fill=ticker)) +
          geom_bar(stat="identity", width=1) +
          coord_polar("y", start=0) +
          labs(title="Portfolio Allocation",
               fill="Ticker") +
          theme_minimal() +
          theme(axis.title.x=element_blank(),
                axis.title.y=element_blank(),
                axis.text.x=element_blank(),
                panel.grid=element_blank()) +
          scale_fill_brewer(palette="Set3")
          
        # Save the plot
        plot_file <- tempfile(fileext=".png")
        ggsave(plot_file, p, width=8, height=7)
        
        # Create results object
        results <- list(plot_path=plot_file)
        """
        
        # Execute R script
        return self.r_executor.execute_script(r_script, {"portfolio_data": portfolio_data})
        
    def export_data(self, data: pd.DataFrame, name: str) -> Dict[str, Any]:
        """
        Export data using the export service.
        
        Args:
            data: DataFrame to export
            name: Base name for the export
            
        Returns:
            Export result dictionary
        """
        if not self.export_service:
            return {"error": "Export service not initialized"}
            
        # Get default path for export
        file_path = self.export_service.get_default_export_path(name)
        
        # Export to CSV
        return self.export_service.export_data(data, file_path)