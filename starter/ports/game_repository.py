"""Port for game state persistence."""

from abc import ABC, abstractmethod
from typing import Optional

from domain.models import GameState


class GameRepository(ABC):
    """Contract for game state storage and retrieval."""
    
    @abstractmethod
    def save(self, game_id: str, state: GameState) -> None:
        """Save game state.
        
        Args:
            game_id: Unique game identifier
            state: Game state to save
        """
        pass
    
    @abstractmethod
    def load(self, game_id: str) -> Optional[GameState]:
        """Load game state.
        
        Args:
            game_id: Unique game identifier
        
        Returns:
            GameState or None if not found
        """
        pass
    
    @abstractmethod
    def delete(self, game_id: str) -> None:
        """Delete game state.
        
        Args:
            game_id: Unique game identifier
        """
        pass
    
    @abstractmethod
    def exists(self, game_id: str) -> bool:
        """Check if game exists.
        
        Args:
            game_id: Unique game identifier
        
        Returns:
            True if game exists
        """
        pass
