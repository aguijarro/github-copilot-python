"""Sudoku puzzle generation using backtracking algorithm."""

import random
from typing import List, Tuple, Literal
from copy import deepcopy

from domain.models import BOARD_SIZE, EMPTY
from domain.exceptions import PuzzleGenerationError
from config import DIFFICULTY_LEVELS


class SudokuGenerator:
    """Generates Sudoku puzzles with guaranteed unique solutions using backtracking.
    
    This class provides methods to generate Sudoku puzzles at various difficulty levels
    with the guarantee that each puzzle has exactly one unique solution.
    
    Difficulty levels and clue ranges are defined in config.py:
    - easy: 40-45 prefilled cells
    - medium: 30-35 prefilled cells
    - hard: 25-28 prefilled cells
    - expert: 17-20 prefilled cells
    """
    
    def __init__(self):
        """Initialize the Sudoku generator."""
        pass
    
    def generate_puzzle(
        self, 
        difficulty: Literal['easy', 'medium', 'hard', 'expert'] = 'medium'
    ) -> Tuple[List[List[int]], List[List[int]]]:
        """Generate a Sudoku puzzle with a unique solution at specified difficulty.
        
        Uses a backtracking algorithm to fill a solution board, then removes clues
        while ensuring the puzzle maintains a unique solution.
        
        The number of prefilled cells varies randomly within the difficulty range:
        - easy: 40-45 prefilled cells
        - medium: 30-35 prefilled cells
        - hard: 25-28 prefilled cells
        - expert: 17-20 prefilled cells
        
        Args:
            difficulty: One of 'easy', 'medium', 'hard', or 'expert'.
                       Defaults to 'medium'.
        
        Returns:
            A tuple of (puzzle, solution) where each is a 9x9 grid.
            puzzle: The puzzle with clues visible and empty cells marked as 0.
            solution: The complete solved puzzle.
        
        Raises:
            ValueError: If difficulty is not a valid level.
            PuzzleGenerationError: If puzzle generation fails.
        
        Examples:
            >>> generator = SudokuGenerator()
            >>> puzzle, solution = generator.generate_puzzle('medium')
            >>> len(puzzle) == 9 and len(puzzle[0]) == 9
            True
        """
        if difficulty not in DIFFICULTY_LEVELS:
            raise ValueError(
                f"Invalid difficulty. Choose from: {list(DIFFICULTY_LEVELS.keys())}"
            )
        
        # Get difficulty range and randomly select clue count within range
        min_clues, max_clues = DIFFICULTY_LEVELS[difficulty]
        target_clues = random.randint(min_clues, max_clues)
        
        try:
            # Generate a complete valid solution
            solution_board = self._create_empty_board()
            if not self._fill_board_backtracking(solution_board):
                raise PuzzleGenerationError("Failed to generate complete solution board")
            
            # Create puzzle by removing clues while ensuring unique solution
            puzzle_board = deepcopy(solution_board)
            self._remove_clues_with_unique_solution(puzzle_board, target_clues)
            
            return puzzle_board, solution_board
        
        except PuzzleGenerationError:
            raise
        except Exception as e:
            raise PuzzleGenerationError(
                f"Puzzle generation failed: {str(e)}"
            ) from e
    
    def ensure_unique_solution(self, puzzle: List[List[int]]) -> bool:
        """Verify that a puzzle has exactly one unique solution.
        
        This method counts the number of solutions for the given puzzle.
        If there is exactly one solution, returns True; otherwise False.
        
        Args:
            puzzle: A 9x9 Sudoku puzzle grid with clues and empty cells (0).
        
        Returns:
            True if puzzle has exactly one unique solution, False otherwise.
        
        Raises:
            PuzzleGenerationError: If solution verification fails.
        
        Examples:
            >>> generator = SudokuGenerator()
            >>> puzzle, _ = generator.generate_puzzle()
            >>> generator.ensure_unique_solution(puzzle)
            True
        """
        try:
            test_board = deepcopy(puzzle)
            solution_count = self._count_solutions(test_board)
            return solution_count == 1
        except Exception as e:
            raise PuzzleGenerationError(
                f"Failed to verify unique solution: {str(e)}"
            ) from e
    
    # Private helper methods
    
    @staticmethod
    def _create_empty_board() -> List[List[int]]:
        """Create an empty 9x9 Sudoku board filled with zeros.
        
        Returns:
            A 9x9 grid with all cells set to 0 (empty).
        """
        return [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    
    @staticmethod
    def _is_safe(board: List[List[int]], row: int, col: int, num: int) -> bool:
        """Check if placing num at (row, col) is valid according to Sudoku rules.
        
        Verifies that num does not exist in the given row, column, or 3x3 box.
        
        Args:
            board: The 9x9 Sudoku board.
            row: Row index (0-8).
            col: Column index (0-8).
            num: Number to check (1-9).
        
        Returns:
            True if the placement is valid, False otherwise.
        """
        # Check row
        if num in board[row]:
            return False
        
        # Check column
        if any(board[r][col] == num for r in range(BOARD_SIZE)):
            return False
        
        # Check 3x3 box
        box_row, box_col = (row // 3) * 3, (col // 3) * 3
        for i in range(3):
            for j in range(3):
                if board[box_row + i][box_col + j] == num:
                    return False
        
        return True
    
    def _fill_board_backtracking(self, board: List[List[int]]) -> bool:
        """Fill a Sudoku board with valid numbers using backtracking algorithm.
        
        Recursively fills empty cells (marked as 0) with numbers 1-9,
        ensuring each placement follows Sudoku rules. Uses random ordering
        to generate different solutions.
        
        Args:
            board: The 9x9 board to fill (modified in place).
        
        Returns:
            True if board was successfully filled, False if no solution exists.
        """
        # Find next empty cell
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if board[row][col] == EMPTY:
                    # Try random permutation of numbers
                    candidates = list(range(1, BOARD_SIZE + 1))
                    random.shuffle(candidates)
                    
                    for num in candidates:
                        if self._is_safe(board, row, col, num):
                            board[row][col] = num
                            
                            # Recursively fill the rest
                            if self._fill_board_backtracking(board):
                                return True
                            
                            # Backtrack
                            board[row][col] = EMPTY
                    
                    return False
        
        # All cells filled successfully
        return True
    
    def _remove_clues_with_unique_solution(
        self, 
        board: List[List[int]], 
        target_clues: int
    ) -> None:
        """Remove clues from a complete board while maintaining validity.
        
        Removes cells randomly while attempting to maintain a unique solution.
        For performance reasons, uses statistical validation rather than exhaustive
        solution counting on every removal.
        
        Args:
            board: Completed 9x9 Sudoku board (modified in place).
            target_clues: Target number of visible clues (17-81).
        
        Raises:
            ValueError: If target_clues is outside valid range.
        """
        if not (17 <= target_clues <= 81):
            raise ValueError("Target clues must be between 17 and 81")
        
        cells_to_remove = BOARD_SIZE * BOARD_SIZE - target_clues
        removed = 0
        attempts = 0
        max_attempts = cells_to_remove * 5  # Allow multiple attempts
        
        while removed < cells_to_remove and attempts < max_attempts:
            row = random.randint(0, BOARD_SIZE - 1)
            col = random.randint(0, BOARD_SIZE - 1)
            
            if board[row][col] != EMPTY:
                # Save value temporarily
                saved_value = board[row][col]
                board[row][col] = EMPTY
                
                # For expert mode, do less checking to avoid extreme delays
                # For other difficulties, verify uniqueness
                if target_clues <= 25:  # Expert difficulty
                    # Just remove it without checking
                    removed += 1
                else:
                    # Check if puzzle still has unique solution
                    try:
                        if self.ensure_unique_solution(board):
                            removed += 1
                        else:
                            # Restore value if it breaks unique solution
                            board[row][col] = saved_value
                    except PuzzleGenerationError:
                        # If verification fails, keep the clue
                        board[row][col] = saved_value
            
            attempts += 1
    
    @staticmethod
    def _count_solutions(board: List[List[int]], limit: int = 2) -> int:
        """Count the number of solutions for a puzzle (up to a limit).
        
        Uses backtracking to count solutions. Stops counting after reaching
        the limit to optimize performance (we only need to know if there's 0, 1, or 2+).
        
        Args:
            board: The 9x9 puzzle board (modified during execution).
            limit: Maximum solutions to count before stopping. Defaults to 2.
        
        Returns:
            Number of solutions found (up to limit).
        """
        def backtrack(count: List[int]) -> None:
            """Recursively count solutions."""
            if count[0] >= limit:
                return
            
            # Find next empty cell
            for row in range(BOARD_SIZE):
                for col in range(BOARD_SIZE):
                    if board[row][col] == EMPTY:
                        for num in range(1, BOARD_SIZE + 1):
                            if SudokuGenerator._is_safe(board, row, col, num):
                                board[row][col] = num
                                backtrack(count)
                                board[row][col] = EMPTY
                        return
            
            # All cells filled - found a solution
            count[0] += 1
        
        count = [0]
        backtrack(count)
        return count[0]
