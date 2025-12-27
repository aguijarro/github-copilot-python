"""Custom exceptions for Sudoku domain logic."""


class SudokuError(Exception):
    """Base exception for Sudoku operations."""
    pass


class ValidationError(SudokuError):
    """Raised when user input validation fails."""
    pass


class PuzzleGenerationError(SudokuError):
    """Raised when puzzle generation fails."""
    pass


class GameStateError(SudokuError):
    """Raised when game state transitions are invalid."""
    pass


class GameNotFoundError(SudokuError):
    """Raised when game is not found."""
    pass
