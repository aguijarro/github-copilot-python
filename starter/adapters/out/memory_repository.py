"""In-memory implementation of GameRepository port."""

from typing import Dict, Optional

from domain.models import GameState
from ports.game_repository import GameRepository


class MemoryGameRepository(GameRepository):
    """In-memory implementation of game state storage.
    
    Thread-safe storage using dictionary with game_id as key.
    """
    
    def __init__(self):
        """Initialize in-memory storage."""
        self._games: Dict[str, GameState] = {}
    
    def save(self, game_id: str, state: GameState) -> None:
        """Save game state to memory.
        
        Args:
            game_id: Unique game identifier
            state: Game state to save
        """
        self._games[game_id] = state
    
    def load(self, game_id: str) -> Optional[GameState]:
        """Load game state from memory.
        
        Args:
            game_id: Unique game identifier
        
        Returns:
            GameState if found, None otherwise
        """
        return self._games.get(game_id)
    
    def delete(self, game_id: str) -> None:
        """Delete game state from memory.
        
        Args:
            game_id: Unique game identifier
        """
        if game_id in self._games:
            del self._games[game_id]
    
    def exists(self, game_id: str) -> bool:
        """Check if game exists in memory.
        
        Args:
            game_id: Unique game identifier
        
        Returns:
            True if game exists
        """
        return game_id in self._games
