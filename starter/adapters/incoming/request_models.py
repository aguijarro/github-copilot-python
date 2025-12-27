"""Request/Response DTOs for HTTP layer."""

from dataclasses import dataclass
from typing import List

from domain.exceptions import ValidationError
from config import DIFFICULTY_LEVELS
import random


@dataclass
class NewGameRequest:
    """Request to start a new game."""
    
    clues: int
    
    @staticmethod
    def from_args(clues_arg, difficulty_arg=None) -> "NewGameRequest":
        """Create from Flask request args.
        
        Args:
            clues_arg: Query parameter for explicit clue count
            difficulty_arg: Query parameter for difficulty level (easy, medium, hard)
        
        Returns:
            NewGameRequest instance
        
        Raises:
            ValidationError: If validation fails
        """
        try:
            # If difficulty is specified, use it to determine clues
            if difficulty_arg:
                if difficulty_arg not in DIFFICULTY_LEVELS:
                    raise ValueError(f"Invalid difficulty. Must be one of: {', '.join(DIFFICULTY_LEVELS.keys())}")
                min_clues, max_clues = DIFFICULTY_LEVELS[difficulty_arg]
                clues = random.randint(min_clues, max_clues)
            # Otherwise use explicit clues parameter
            elif clues_arg:
                clues = int(clues_arg)
                if not (17 <= clues <= 81):
                    raise ValueError("Clues must be between 17 and 81")
            # Default to medium difficulty
            else:
                min_clues, max_clues = DIFFICULTY_LEVELS['medium']
                clues = random.randint(min_clues, max_clues)
            
            return NewGameRequest(clues=clues)
        except (ValueError, TypeError) as e:
            raise ValidationError(f"Invalid game parameters: {str(e)}")


@dataclass
class CheckSolutionRequest:
    """Request to check a solution."""
    
    board: List[List[int]]
    
    @staticmethod
    def from_json(data: dict) -> "CheckSolutionRequest":
        """Create from JSON request body.
        
        Args:
            data: JSON request data
        
        Returns:
            CheckSolutionRequest instance
        
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(data, dict):
            raise ValidationError("Request body must be JSON object")
        
        board = data.get('board')
        if board is None:
            raise ValidationError("Missing 'board' field")
        
        if not isinstance(board, list):
            raise ValidationError("Board must be a list")
        
        if len(board) != 9:
            raise ValidationError("Board must have 9 rows")
        
        for i, row in enumerate(board):
            if not isinstance(row, list):
                raise ValidationError(f"Row {i} must be a list")
            if len(row) != 9:
                raise ValidationError(f"Row {i} must have 9 columns")
            for j, cell in enumerate(row):
                if not isinstance(cell, int):
                    raise ValidationError(f"Cell [{i}][{j}] must be an integer")
                if not (0 <= cell <= 9):
                    raise ValidationError(f"Cell [{i}][{j}] must be between 0 and 9")
        
        return CheckSolutionRequest(board=board)


@dataclass
class NewGameResponse:
    """Response to new game request."""
    
    puzzle: List[List[int]]
    game_id: str = ""
    
    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        return {
            'puzzle': self.puzzle,
            'game_id': self.game_id
        }


@dataclass
class CheckSolutionResponse:
    """Response to check solution request."""
    
    is_correct: bool
    incorrect_cells: List[List[int]]
    message: str = ""
    
    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        return {
            'is_correct': self.is_correct,
            'incorrect': self.incorrect_cells,
            'message': self.message
        }


@dataclass
class ErrorResponse:
    """Error response."""
    
    error: str
    code: str = "ERROR"
    details: str = ""
    
    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        return {
            'error': self.error,
            'code': self.code,
            'details': self.details
        }
