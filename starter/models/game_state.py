"""Game state dataclass for managing Sudoku game state."""

from dataclasses import dataclass, field, asdict
from typing import List, Tuple, Dict, Optional, Any
from datetime import datetime
from copy import deepcopy

from domain.models import BOARD_SIZE, EMPTY


@dataclass
class GameState:
    """Represents the complete state of a Sudoku game session.
    
    Manages all aspects of a game including the board, difficulty, timing,
    hints, and locked cells. Provides serialization/deserialization.
    
    Attributes:
        board: Current 9x9 game board with player's moves
        difficulty: Game difficulty level ('easy', 'medium', 'hard', 'expert')
        start_time: Timestamp when the game started
        hints_used: Number of hints revealed to the player
        locked_cells: Set of (row, col) tuples representing initially given clues
        is_complete: Whether the board is completely filled
    """
    
    board: List[List[int]]
    difficulty: str
    start_time: datetime
    hints_used: int = 0
    locked_cells: List[Tuple[int, int]] = field(default_factory=list)
    is_complete: bool = False
    
    def __post_init__(self):
        """Validate board dimensions and initialize locked_cells."""
        if len(self.board) != BOARD_SIZE:
            raise ValueError(f"Board must have {BOARD_SIZE} rows")
        for row in self.board:
            if len(row) != BOARD_SIZE:
                raise ValueError(f"Each row must have {BOARD_SIZE} columns")
        
        # Initialize locked_cells if empty - cells with non-zero values are locked
        if not self.locked_cells:
            self.locked_cells = [
                (row, col)
                for row in range(BOARD_SIZE)
                for col in range(BOARD_SIZE)
                if self.board[row][col] != EMPTY
            ]
    
    def get_elapsed_time(self) -> int:
        """Get elapsed time in seconds since game started.
        
        Returns:
            Elapsed time in seconds
            
        Examples:
            >>> import time
            >>> gs = GameState(...start_time=datetime.now()...)
            >>> time.sleep(1)
            >>> elapsed = gs.get_elapsed_time()
            >>> elapsed >= 1
            True
        """
        return int((datetime.now() - self.start_time).total_seconds())
    
    def is_cell_locked(self, row: int, col: int) -> bool:
        """Check if a cell is locked (initial clue).
        
        Locked cells cannot be modified by the player.
        
        Args:
            row: Row index (0-8)
            col: Column index (0-8)
        
        Returns:
            True if cell is locked, False otherwise
            
        Raises:
            ValueError: If position is invalid
            
        Examples:
            >>> gs = GameState(board=[[5,0,0,...], ...], ...)
            >>> gs.is_cell_locked(0, 0)
            True
            >>> gs.is_cell_locked(0, 1)
            False
        """
        if not (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE):
            raise ValueError(f"Invalid position: ({row}, {col})")
        return (row, col) in self.locked_cells
    
    def get_locked_cells_count(self) -> int:
        """Get the total number of locked cells in the game.
        
        Returns:
            Count of locked (initial clue) cells
        """
        return len(self.locked_cells)
    
    def get_filled_cells_count(self) -> int:
        """Get the total number of filled cells (locked + player-filled).
        
        Returns:
            Count of non-empty cells in current board
        """
        return sum(1 for row in self.board for cell in row if cell != EMPTY)
    
    def get_empty_cells_count(self) -> int:
        """Get the total number of empty cells remaining.
        
        Returns:
            Count of empty cells (value 0)
        """
        return sum(1 for row in self.board for cell in row if cell == EMPTY)
    
    def get_progress_percentage(self) -> float:
        """Get game progress as a percentage (0-100).
        
        Returns:
            Progress percentage (0.0 to 100.0)
        """
        total_cells = BOARD_SIZE * BOARD_SIZE
        filled = self.get_filled_cells_count()
        return (filled / total_cells) * 100.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert GameState to dictionary for serialization.
        
        Converts all fields to JSON-serializable types, including:
        - datetime to ISO format string
        - locked_cells List[Tuple] to List[List]
        - Maintains board as nested list
        
        Returns:
            Dictionary representation of GameState
            
        Examples:
            >>> gs = GameState(...)
            >>> data = gs.to_dict()
            >>> 'board' in data and 'difficulty' in data
            True
            >>> isinstance(data['start_time'], str)
            True
        """
        return {
            'board': [row[:] for row in self.board],
            'difficulty': self.difficulty,
            'start_time': self.start_time.isoformat(),
            'hints_used': self.hints_used,
            'locked_cells': [list(cell) for cell in self.locked_cells],
            'is_complete': self.is_complete,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameState':
        """Create GameState instance from dictionary.
        
        Restores all fields from serialized data, including:
        - ISO format string to datetime
        - List[List] locked_cells back to List[Tuple]
        - Board as nested list
        
        Args:
            data: Dictionary with GameState fields
        
        Returns:
            GameState instance reconstructed from data
            
        Raises:
            KeyError: If required fields are missing
            ValueError: If data is invalid (bad board size, invalid difficulty, etc.)
            
        Examples:
            >>> original = GameState(...)
            >>> data = original.to_dict()
            >>> restored = GameState.from_dict(data)
            >>> restored.board == original.board
            True
        """
        # Parse start_time from ISO format string
        if isinstance(data['start_time'], str):
            start_time = datetime.fromisoformat(data['start_time'])
        else:
            start_time = data['start_time']
        
        # Convert locked_cells from list of lists to list of tuples
        locked_cells = [tuple(cell) for cell in data.get('locked_cells', [])]
        
        return cls(
            board=deepcopy(data['board']),
            difficulty=data['difficulty'],
            start_time=start_time,
            hints_used=data.get('hints_used', 0),
            locked_cells=locked_cells,
            is_complete=data.get('is_complete', False),
        )
    
    def copy(self) -> 'GameState':
        """Create a deep copy of the GameState.
        
        Returns:
            Independent copy of the current GameState
            
        Examples:
            >>> original = GameState(...)
            >>> copy_state = original.copy()
            >>> copy_state.board[0][0] = 999
            >>> original.board[0][0] != 999
            True
        """
        return GameState(
            board=deepcopy(self.board),
            difficulty=self.difficulty,
            start_time=self.start_time,
            hints_used=self.hints_used,
            locked_cells=list(self.locked_cells),
            is_complete=self.is_complete,
        )
    
    def unlock_cell(self, row: int, col: int) -> bool:
        """Unlock a previously locked cell (for admin/debug purposes).
        
        Args:
            row: Row index (0-8)
            col: Column index (0-8)
        
        Returns:
            True if cell was unlocked, False if not previously locked
            
        Raises:
            ValueError: If position is invalid
        """
        if not (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE):
            raise ValueError(f"Invalid position: ({row}, {col})")
        
        cell_tuple = (row, col)
        if cell_tuple in self.locked_cells:
            self.locked_cells.remove(cell_tuple)
            return True
        return False
    
    def lock_cell(self, row: int, col: int) -> bool:
        """Lock a cell (prevent further modifications).
        
        Args:
            row: Row index (0-8)
            col: Column index (0-8)
        
        Returns:
            True if cell was locked, False if already locked
            
        Raises:
            ValueError: If position is invalid
        """
        if not (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE):
            raise ValueError(f"Invalid position: ({row}, {col})")
        
        cell_tuple = (row, col)
        if cell_tuple not in self.locked_cells:
            self.locked_cells.append(cell_tuple)
            return True
        return False
