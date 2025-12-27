"""Domain models for Sudoku game."""

from dataclasses import dataclass, field
from typing import List
from datetime import datetime


BOARD_SIZE = 9
EMPTY = 0


@dataclass
class SudokuBoard:
    """Represents a 9x9 Sudoku board."""
    
    grid: List[List[int]]
    
    def __post_init__(self):
        """Validate board dimensions."""
        if len(self.grid) != BOARD_SIZE:
            raise ValueError(f"Board must have {BOARD_SIZE} rows")
        for row in self.grid:
            if len(row) != BOARD_SIZE:
                raise ValueError(f"Each row must have {BOARD_SIZE} columns")
    
    def get_cell(self, row: int, col: int) -> int:
        """Get value at cell position."""
        return self.grid[row][col]
    
    def set_cell(self, row: int, col: int, value: int) -> None:
        """Set value at cell position."""
        if not (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE):
            raise ValueError(f"Invalid position: ({row}, {col})")
        if not (0 <= value <= BOARD_SIZE):
            raise ValueError(f"Invalid value: {value}")
        self.grid[row][col] = value
    
    def copy(self) -> "SudokuBoard":
        """Create a deep copy of the board."""
        grid_copy = [row[:] for row in self.grid]
        return SudokuBoard(grid_copy)


@dataclass
class GameState:
    """Represents the state of a Sudoku game."""
    
    game_id: str
    puzzle: SudokuBoard
    solution: SudokuBoard
    current_board: SudokuBoard
    difficulty: str = "medium"
    moves: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def is_complete(self) -> bool:
        """Check if puzzle is completely filled."""
        for row in self.current_board.grid:
            for cell in row:
                if cell == EMPTY:
                    return False
        return True
    
    def is_correct(self) -> bool:
        """Check if current board matches solution."""
        if not self.is_complete():
            return False
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if self.current_board.get_cell(i, j) != self.solution.get_cell(i, j):
                    return False
        return True


@dataclass
class CheckResult:
    """Result of checking a solution."""
    
    is_correct: bool
    incorrect_cells: List[tuple]
    message: str = ""
