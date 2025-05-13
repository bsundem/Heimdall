from typing import Dict, List, Any, Optional, Callable
import logging
from PySide6 import QtCore, QtWidgets
import threading
import asyncio

class AsyncWorker(QtCore.QObject):
    """
    Worker that runs tasks asynchronously.
    """
    taskFinished = QtCore.Signal(object)
    taskError = QtCore.Signal(str)
    
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        
    def run(self):
        try:
            if asyncio.iscoroutinefunction(self.func):
                # Create a new event loop for this thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(self.func(*self.args, **self.kwargs))
                loop.close()
            else:
                # Run regular function
                result = self.func(*self.args, **self.kwargs)
                
            self.taskFinished.emit(result)
        except Exception as e:
            self.taskError.emit(str(e))

class AsyncWidget(QtWidgets.QWidget):
    """
    Base widget that supports asynchronous operations.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.tasks = []
        
    def run_async(self, func, *args, on_complete=None, on_error=None, **kwargs):
        """
        Run a function asynchronously.
        
        Args:
            func: The function to run
            *args: Arguments to pass to the function
            on_complete: Callback to run when the task completes successfully
            on_error: Callback to run when the task fails
            **kwargs: Keyword arguments to pass to the function
            
        Returns:
            The worker that is running the task
        """
        thread = QtCore.QThread()
        worker = AsyncWorker(func, *args, **kwargs)
        worker.moveToThread(thread)
        
        # Connect signals
        thread.started.connect(worker.run)
        worker.taskFinished.connect(lambda result: self._on_task_complete(thread, worker, result, on_complete))
        worker.taskError.connect(lambda error: self._on_task_error(thread, worker, error, on_error))
        
        # Store reference to prevent garbage collection
        self.tasks.append((thread, worker))
        
        # Start thread
        thread.start()
        
        return worker
        
    def _on_task_complete(self, thread, worker, result, callback):
        """
        Handle task completion.
        """
        thread.quit()
        if callback:
            callback(result)
        # Clean up
        self._cleanup_task(thread, worker)
            
    def _on_task_error(self, thread, worker, error, callback):
        """
        Handle task error.
        """
        thread.quit()
        self.logger.error(f"Async task error: {error}")
        if callback:
            callback(error)
        else:
            # Show error message if no callback provided
            QtWidgets.QMessageBox.critical(self, "Error", f"An error occurred: {error}")
        # Clean up
        self._cleanup_task(thread, worker)
            
    def _cleanup_task(self, thread, worker):
        """
        Clean up a completed task.
        """
        if (thread, worker) in self.tasks:
            self.tasks.remove((thread, worker))