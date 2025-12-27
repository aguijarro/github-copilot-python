"""Puzzle generation implementation."""

from typing import Tuple, List

from domain.sudoku_game import generate_puzzle as domain_generate_puzzle
from ports.puzzle_generator import PuzzleGenerator


class RandomPuzzleGenerator(PuzzleGenerator):
    """Generates random Sudoku puzzles using domain logic."""
    
    def generate(self, clues: int) -> Tuple[List[List[int]], List[List[int]]]:
        """Generate a Sudoku puzzle with solution.
        
        Args:
            clues: Number of visible clues (17-81)
        
        Returns:
            Tuple of (puzzle, solution) boards
        
        Raises:
            ValueError: If clue count is invalid
            PuzzleGenerationError: If generation fails
        """
        return domain_generate_puzzle(clues)
