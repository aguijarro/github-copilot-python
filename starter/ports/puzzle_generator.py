"""Port for puzzle generation."""

from abc import ABC, abstractmethod
from typing import Tuple, List


class PuzzleGenerator(ABC):
    """Contract for puzzle generation service."""
    
    @abstractmethod
    def generate(self, clues: int) -> Tuple[List[List[int]], List[List[int]]]:
        """Generate a Sudoku puzzle with solution.
        
        Args:
            clues: Number of visible clues (17-81)
        
        Returns:
            Tuple of (puzzle, solution) boards
        """
        pass
