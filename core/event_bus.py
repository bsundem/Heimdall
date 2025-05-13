from typing import Dict, List, Any, Callable, Optional
import logging
import asyncio
from collections import defaultdict

class Event:
    """
    Base class for all events in the system.
    """
    def __init__(self, event_type: str, data: Optional[Dict[str, Any]] = None):
        self.event_type = event_type
        self.data = data or {}
        
class EventBus:
    """
    Facilitates communication between decoupled components using a publish-subscribe pattern.
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.subscribers = defaultdict(list)
        self.loop = None
        
    def initialize(self) -> None:
        """
        Initialize the event bus.
        """
        self.logger.info("Initializing event bus")
        try:
            self.loop = asyncio.get_event_loop()
        except RuntimeError:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
        
    def shutdown(self) -> None:
        """
        Shutdown the event bus.
        """
        self.logger.info("Shutting down event bus")
        # Clean up subscribers
        self.subscribers.clear()
        
    def subscribe(self, event_type: str, callback: Callable[[Event], None], priority: int = 0) -> None:
        """
        Subscribe to an event type.
        
        Args:
            event_type: The type of event to subscribe to
            callback: The function to call when the event is published
            priority: The priority of the subscriber (higher values get called first)
        """
        self.subscribers[event_type].append((callback, priority))
        self.subscribers[event_type].sort(key=lambda x: -x[1])  # Sort by priority (higher first)
        self.logger.debug(f"Subscribed to event: {event_type}")
        
    def unsubscribe(self, event_type: str, callback: Callable[[Event], None]) -> None:
        """
        Unsubscribe from an event type.
        """
        if event_type in self.subscribers:
            self.subscribers[event_type] = [
                (cb, prio) for cb, prio in self.subscribers[event_type] 
                if cb != callback
            ]
            self.logger.debug(f"Unsubscribed from event: {event_type}")
            
    def publish(self, event: Event) -> None:
        """
        Publish an event synchronously.
        """
        if event.event_type in self.subscribers:
            for callback, _ in self.subscribers[event.event_type]:
                try:
                    callback(event)
                except Exception as e:
                    self.logger.error(f"Error in event handler: {e}")
                    
    async def publish_async(self, event: Event) -> None:
        """
        Publish an event asynchronously.
        """
        if event.event_type in self.subscribers:
            for callback, _ in self.subscribers[event.event_type]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(event)
                    else:
                        self.loop.run_in_executor(None, callback, event)
                except Exception as e:
                    self.logger.error(f"Error in async event handler: {e}")