"""
Shared memory system for agent communication.

This module provides a centralized memory system that allows agents
to share context and data during processing.
"""

import json
from typing import Any, Dict, List, Optional
from datetime import datetime
from collections import deque


class SharedMemory:
    """
    Centralized memory system for agent communication.
    
    Provides a shared context that all agents can access and modify
    during the import clearance process.
    """
    
    def __init__(self, max_history: int = 100):
        self._data: Dict[str, Any] = {}
        self._history: deque = deque(maxlen=max_history)
        self._timestamps: Dict[str, datetime] = {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from memory."""
        return self._data.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set value in memory with timestamp."""
        self._data[key] = value
        self._timestamps[key] = datetime.now()
        self._history.append({
            "action": "set",
            "key": key,
            "value": str(value)[:100],  # Truncate for logging
            "timestamp": self._timestamps[key].isoformat()
        })
    
    def update(self, data: Dict[str, Any]) -> None:
        """Update multiple values in memory."""
        for key, value in data.items():
            self.set(key, value)
    
    def delete(self, key: str) -> bool:
        """Delete a key from memory."""
        if key in self._data:
            del self._data[key]
            del self._timestamps[key]
            return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Return all memory data as dictionary."""
        return dict(self._data)
    
    def get_history(self, limit: int = 10) -> List[Dict]:
        """Get recent history entries."""
        return list(self._history)[-limit:]
    
    def clear(self) -> None:
        """Clear all memory data."""
        self._data.clear()
        self._timestamps.clear()
        self._history.clear()


class AgentContext:
    """
    Context wrapper for individual agents.
    
    Provides agent-specific access to shared memory with
    additional agent-specific storage.
    """
    
    def __init__(self, agent_name: str, memory: SharedMemory):
        self.agent_name = agent_name
        self.memory = memory
        self._local_storage: Dict[str, Any] = {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from shared memory."""
        return self.memory.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set value in shared memory."""
        self.memory.set(key, value)
    
    def get_local(self, key: str, default: Any = None) -> Any:
        """Get value from local agent storage."""
        return self._local_storage.get(key, default)
    
    def set_local(self, key: str, value: Any) -> None:
        """Set value in local agent storage."""
        self._local_storage[key] = value
    
    def log(self, message: str, level: str = "INFO") -> None:
        """Log a message with agent context."""
        timestamp = datetime.now().isoformat()
        print(f"[{timestamp}] [{self.agent_name}] [{level}] {message}")