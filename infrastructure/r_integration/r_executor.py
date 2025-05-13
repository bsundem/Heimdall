from typing import Dict, List, Any, Optional, Union
import logging
import tempfile
import pandas as pd
import os
import uuid
import asyncio
from concurrent.futures import ProcessPoolExecutor

class RExecutor:
    """
    Enables execution of R scripts from Python.
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.process_pool = ProcessPoolExecutor(max_workers=2)
        
    def initialize(self) -> None:
        """
        Initialize the R executor.
        """
        self.logger.info("Initializing R executor")
        try:
            # Check if rpy2 is available
            import rpy2.robjects as robjects
            self.r_available = True
            self.logger.info("R integration initialized successfully")
        except ImportError:
            self.r_available = False
            self.logger.warning("rpy2 not available. R integration will be disabled.")
        
    def shutdown(self) -> None:
        """
        Shutdown the R executor.
        """
        self.logger.info("Shutting down R executor")
        self.process_pool.shutdown()
        
    def execute_script(self, script: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute an R script synchronously.
        
        Args:
            script: The R script to execute
            data: Optional data to pass to the R script
            
        Returns:
            A dictionary with the results of the script execution
        """
        if not self.r_available:
            self.logger.error("R integration not available")
            return {"error": "R integration not available"}
            
        try:
            import rpy2.robjects as robjects
            from rpy2.robjects import pandas2ri
            from rpy2.robjects.conversion import localconverter
            
            # Create a unique temporary file to store the script
            script_file = tempfile.NamedTemporaryFile(delete=False, suffix='.R')
            try:
                with open(script_file.name, 'w') as f:
                    f.write(script)
                
                # Initialize results container
                results = {}
                
                # Convert Python data to R
                r_env = robjects.globalenv
                
                if data:
                    with localconverter(robjects.default_converter + pandas2ri.converter):
                        for key, value in data.items():
                            if isinstance(value, pd.DataFrame):
                                r_env[key] = value
                            elif isinstance(value, (list, tuple)):
                                r_env[key] = robjects.vectors.StrVector(value) if all(isinstance(x, str) for x in value) else robjects.vectors.FloatVector(value)
                            elif isinstance(value, (int, float, bool, str)):
                                r_env[key] = robjects.vectors.FloatVector([value]) if isinstance(value, (int, float)) else robjects.vectors.StrVector([str(value)])
                
                # Execute the script
                robjects.r.source(script_file.name)
                
                # Get results from R
                # We'll look for a predefined list or environment called 'results'
                try:
                    r_results = robjects.globalenv['results']
                    
                    # Convert R results to Python
                    if isinstance(r_results, robjects.Environment):
                        for key in r_results.keys():
                            value = r_results[key]
                            # Convert DataFrames
                            if hasattr(value, 'to_pandas'):
                                results[key] = value.to_pandas()
                            else:
                                results[key] = value
                    elif isinstance(r_results, robjects.vectors.ListVector):
                        for i, name in enumerate(r_results.names):
                            value = r_results[i]
                            # Convert DataFrames
                            if hasattr(value, 'to_pandas'):
                                results[name] = value.to_pandas()
                            else:
                                results[name] = value
                except:
                    # If no 'results' object found, return any plots as images
                    try:
                        plot_file = os.path.join(tempfile.gettempdir(), f"plot_{uuid.uuid4()}.png")
                        robjects.r(f'png("{plot_file}")')
                        robjects.r('replayPlot(recordPlot())')
                        robjects.r('dev.off()')
                        results['plot'] = plot_file
                    except:
                        pass
            
            finally:
                # Clean up temporary file
                try:
                    os.unlink(script_file.name)
                except:
                    pass
                
            return results
        
        except Exception as e:
            self.logger.error(f"Error executing R script: {e}")
            return {"error": str(e)}
            
    async def execute_script_async(self, script: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute an R script asynchronously.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.process_pool, 
            self.execute_script, 
            script, 
            data
        )