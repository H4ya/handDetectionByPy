from typing import Any

class CustomError(Exception):
    """Base exception for custom runtime errors."""
    
    def __init__(self, message: str, value: Any) -> None:
        super().__init__(message)  # Passes message to Exception base class
        self.message = message
        self.value = value
        
    def __str__(self) -> str:
        return f"{self.message} (Value: {self.value})"