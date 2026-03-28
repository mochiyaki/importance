"""
Core agent base class for the Importance clearance system.

This module provides the base Agent class that all specialized agents
must inherit from.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from datetime import datetime


class AgentResult:
    """Result container for agent processing."""
    
    def __init__(
        self,
        success: bool,
        data: Optional[Dict[str, Any]] = None,
        errors: Optional[list] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.success = success
        self.data = data or {}
        self.errors = errors or []
        self.metadata = metadata or {}
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "success": self.success,
            "data": self.data,
            "errors": self.errors,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }


class BaseAgent(ABC):
    """Base class for all agents in the Importance system."""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}
        self.context = None
    
    def set_context(self, context: Any) -> None:
        """Set shared context for agent communication."""
        self.context = context
    
    @abstractmethod
    def process(self, input_data: Any) -> AgentResult:
        """
        Process input data and return result.
        
        Args:
            input_data: Input data to process
            
        Returns:
            AgentResult with processing results
        """
        pass
    
    def validate_input(self, input_data: Any) -> bool:
        """
        Validate input data before processing.
        
        Args:
            input_data: Data to validate
            
        Returns:
            True if input is valid, False otherwise
        """
        return input_data is not None
    
    def log_error(self, error: str) -> None:
        """Log an error with agent name prefix."""
        print(f"[{self.name}] Error: {error}")
    
    def log_info(self, message: str) -> None:
        """Log an info message with agent name prefix."""
        print(f"[{self.name}] {message}")