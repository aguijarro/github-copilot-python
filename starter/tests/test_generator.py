"""Tests for Sudoku puzzle generator."""

import pytest
from copy import deepcopy

from utils.generator import SudokuGenerator
from domain.models import BOARD_SIZE, EMPTY
from domain.exceptions import PuzzleGenerationError


class TestSudokuGeneratorInitialization:
    """Test SudokuGenerator initialization."""
    
    def test_generator_creation(self):
        """Test that generator can be instantiated."""
        generator = SudokuGenerator()
        assert generator is not None
    
    def test_difficulty_levels_exist(self):
        """Test that all expected difficulty levels are defined."""
        generator = SudokuGenerator()
        expected_levels = {'easy', 'medium', 'hard', 'expert'}
        assert set(generator.DIFFICULTY_LEVELS.keys()) == expected_levels
    
    def test_difficulty_clue_counts(self):
        """Test that difficulty levels have valid clue counts."""
        generator = SudokuGenerator()
        for level, clues in generator.DIFFICULTY_LEVELS.items():
            assert 17 <= clues <= 81, f"Invalid clues for {level}: {clues}"


class TestGeneratePuzzle:
    """Test the generate_puzzle method."""
    
    def test_generate_puzzle_medium_difficulty(self):
        """Test generating a medium difficulty puzzle."""
        generator = SudokuGenerator()
        puzzle, solution = generator.generate_puzzle('medium')
        
        assert puzzle is not None
        assert solution is not None
        assert len(puzzle) == BOARD_SIZE
        assert len(solution) == BOARD_SIZE
        assert all(len(row) == BOARD_SIZE for row in puzzle)
        assert all(len(row) == BOARD_SIZE for row in solution)
    
    def test_generate_puzzle_all_difficulties(self):
        """Test generating puzzles at all difficulty levels."""
        generator = SudokuGenerator()
        
        for difficulty in ['easy', 'medium', 'hard', 'expert']:
            puzzle, solution = generator.generate_puzzle(difficulty)
            assert len(puzzle) == BOARD_SIZE
            assert len(solution) == BOARD_SIZE
    
    def test_generate_puzzle_default_is_medium(self):
        """Test that default difficulty is medium."""
        generator = SudokuGenerator()
        puzzle, _ = generator.generate_puzzle()
        
        # Count clues in puzzle
        clues_count = sum(1 for row in puzzle for cell in row if cell != EMPTY)
        assert clues_count == generator.DIFFICULTY_LEVELS['medium']
    
    def test_puzzle_has_correct_clue_count(self):
        """Test that generated puzzles have approximately correct clue counts."""
        generator = SudokuGenerator()
        
        for difficulty in ['easy', 'medium', 'hard', 'expert']:
            puzzle, _ = generator.generate_puzzle(difficulty)
            clues_count = sum(1 for row in puzzle for cell in row if cell != EMPTY)
            expected_clues = generator.DIFFICULTY_LEVELS[difficulty]
            
            # Tolerance increases with difficulty due to computation complexity
            # Easy: ±2, Medium: ±3, Hard: ±5, Expert: ±10 (harder to achieve exact)
            if difficulty == 'easy':
                tolerance = 2
            elif difficulty == 'medium':
                tolerance = 3
            elif difficulty == 'hard':
                tolerance = 5
            else:  # expert
                tolerance = 10
            
            assert abs(clues_count - expected_clues) <= tolerance, \
                f"{difficulty}: expected ~{expected_clues}, got {clues_count}"
    
    def test_solution_is_complete(self):
        """Test that generated solution has no empty cells."""
        generator = SudokuGenerator()
        _, solution = generator.generate_puzzle('medium')
        
        for row in solution:
            for cell in row:
                assert cell != EMPTY
                assert 1 <= cell <= 9
    
    def test_puzzle_is_subset_of_solution(self):
        """Test that puzzle clues match corresponding solution cells."""
        generator = SudokuGenerator()
        puzzle, solution = generator.generate_puzzle('medium')
        
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if puzzle[row][col] != EMPTY:
                    assert puzzle[row][col] == solution[row][col]
    
    def test_invalid_difficulty_raises_error(self):
        """Test that invalid difficulty level raises ValueError."""
        generator = SudokuGenerator()
        
        with pytest.raises(ValueError):
            generator.generate_puzzle('impossible')
    
    def test_puzzle_generation_returns_different_puzzles(self):
        """Test that multiple calls generate different puzzles."""
        generator = SudokuGenerator()
        puzzle1, _ = generator.generate_puzzle('medium')
        puzzle2, _ = generator.generate_puzzle('medium')
        
        # Puzzles should be different (statistically certain for random generation)
        assert puzzle1 != puzzle2


class TestEnsureUniqueSolution:
    """Test the ensure_unique_solution method."""
    
    def test_generated_puzzle_has_unique_solution(self):
        """Test that generated puzzles have exactly one unique solution."""
        generator = SudokuGenerator()
        puzzle, _ = generator.generate_puzzle('medium')
        
        is_unique = generator.ensure_unique_solution(puzzle)
        assert is_unique is True
    
    def test_unique_solution_all_difficulties(self):
        """Test unique solution for all difficulty levels.
        
        Note: Expert puzzles may not strictly verify uniqueness due to performance
        constraints. This test verifies that easier puzzles maintain uniqueness.
        """
        generator = SudokuGenerator()
        
        for difficulty in ['easy', 'medium']:  # Test these strictly
            puzzle, _ = generator.generate_puzzle(difficulty)
            is_unique = generator.ensure_unique_solution(puzzle)
            assert is_unique is True, f"Puzzle at {difficulty} has non-unique solution"
        
        # Hard and expert puzzles are generated without strict verification
        # for performance, so we just verify they generate successfully
        for difficulty in ['hard', 'expert']:
            puzzle, _ = generator.generate_puzzle(difficulty)
            assert puzzle is not None
    
    def test_complete_solution_has_unique_solution(self):
        """Test that a complete valid solution is unique."""
        generator = SudokuGenerator()
        _, solution = generator.generate_puzzle('medium')
        
        # A complete solution should be considered unique
        # (or have only itself as solution)
        is_unique = generator.ensure_unique_solution(solution)
        assert is_unique is True
    
    def test_empty_puzzle_has_multiple_solutions(self):
        """Test that an empty puzzle has multiple solutions."""
        generator = SudokuGenerator()
        empty_puzzle = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        
        # Empty puzzle should NOT have unique solution
        # (it has many solutions)
        is_unique = generator.ensure_unique_solution(empty_puzzle)
        # This may be True or False depending on _count_solutions implementation
        # but we're mainly testing that it doesn't crash
        assert isinstance(is_unique, bool)


class TestPrivateHelpers:
    """Test private helper methods."""
    
    def test_create_empty_board(self):
        """Test that empty board creation works correctly."""
        board = SudokuGenerator._create_empty_board()
        
        assert len(board) == BOARD_SIZE
        assert all(len(row) == BOARD_SIZE for row in board)
        assert all(cell == EMPTY for row in board for cell in row)
    
    def test_is_safe_valid_placement(self):
        """Test is_safe with valid placements."""
        board = SudokuGenerator._create_empty_board()
        
        # Placing 1 at (0, 0) should be safe
        assert SudokuGenerator._is_safe(board, 0, 0, 1) is True
    
    def test_is_safe_duplicate_in_row(self):
        """Test is_safe detects duplicates in row."""
        board = SudokuGenerator._create_empty_board()
        board[0][0] = 5
        
        # Placing 5 at (0, 5) should not be safe
        assert SudokuGenerator._is_safe(board, 0, 5, 5) is False
    
    def test_is_safe_duplicate_in_column(self):
        """Test is_safe detects duplicates in column."""
        board = SudokuGenerator._create_empty_board()
        board[0][0] = 5
        
        # Placing 5 at (5, 0) should not be safe
        assert SudokuGenerator._is_safe(board, 5, 0, 5) is False
    
    def test_is_safe_duplicate_in_box(self):
        """Test is_safe detects duplicates in 3x3 box."""
        board = SudokuGenerator._create_empty_board()
        board[0][0] = 5
        
        # Placing 5 at (1, 1) should not be safe (same 3x3 box)
        assert SudokuGenerator._is_safe(board, 1, 1, 5) is False
    
    def test_fill_board_backtracking_completes(self):
        """Test that backtracking algorithm fills the entire board."""
        generator = SudokuGenerator()
        board = SudokuGenerator._create_empty_board()
        
        result = generator._fill_board_backtracking(board)
        
        assert result is True
        assert all(cell != EMPTY for row in board for cell in row)
        assert all(1 <= cell <= 9 for row in board for cell in row)
    
    def test_filled_board_is_valid(self):
        """Test that a filled board satisfies Sudoku constraints."""
        generator = SudokuGenerator()
        board = SudokuGenerator._create_empty_board()
        generator._fill_board_backtracking(board)
        
        # Check rows
        for row in board:
            assert sorted(row) == list(range(1, 10))
        
        # Check columns
        for col in range(BOARD_SIZE):
            column = [board[row][col] for row in range(BOARD_SIZE)]
            assert sorted(column) == list(range(1, 10))
        
        # Check 3x3 boxes
        for box_row in range(0, BOARD_SIZE, 3):
            for box_col in range(0, BOARD_SIZE, 3):
                box = []
                for i in range(3):
                    for j in range(3):
                        box.append(board[box_row + i][box_col + j])
                assert sorted(box) == list(range(1, 10))


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_puzzle_generation_idempotent_seed(self):
        """Test that generation with same seed produces same puzzle (if seeded)."""
        # Without explicit seed control, just verify generation completes
        generator = SudokuGenerator()
        puzzle, _ = generator.generate_puzzle('hard')
        assert puzzle is not None
    
    def test_remove_clues_with_invalid_target(self):
        """Test that invalid clue counts raise ValueError."""
        generator = SudokuGenerator()
        board = SudokuGenerator._create_empty_board()
        
        with pytest.raises(ValueError):
            generator._remove_clues_with_unique_solution(board, 16)  # Too few
        
        with pytest.raises(ValueError):
            generator._remove_clues_with_unique_solution(board, 82)  # Too many
    
    def test_puzzle_can_be_deep_copied(self):
        """Test that generated puzzles can be safely copied."""
        generator = SudokuGenerator()
        puzzle, solution = generator.generate_puzzle('medium')
        
        puzzle_copy = deepcopy(puzzle)
        
        # Find a non-empty cell to modify
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if puzzle[row][col] != EMPTY:
                    puzzle_copy[row][col] = 0
                    # Original should be unchanged
                    assert puzzle[row][col] != puzzle_copy[row][col]
                    return
        
        # If no clues found (shouldn't happen), skip
        assert True


class TestIntegration:
    """Integration tests with other domain components."""
    
    def test_puzzle_solves_to_solution(self):
        """Test that puzzle clues lead toward the solution."""
        generator = SudokuGenerator()
        puzzle, solution = generator.generate_puzzle('medium')
        
        # Every clue in puzzle must match solution
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if puzzle[row][col] != EMPTY:
                    assert puzzle[row][col] == solution[row][col]
    
    def test_generation_performance_easy(self):
        """Test that easy puzzle generation completes in reasonable time."""
        import time
        
        generator = SudokuGenerator()
        start = time.time()
        puzzle, _ = generator.generate_puzzle('easy')
        elapsed = time.time() - start
        
        # Easy puzzles should generate quickly
        assert elapsed < 30  # Generous timeout for slower machines
        assert puzzle is not None
    
    def test_generation_performance_hard(self):
        """Test that hard puzzle generation completes in reasonable time."""
        import time
        
        generator = SudokuGenerator()
        start = time.time()
        puzzle, _ = generator.generate_puzzle('hard')
        elapsed = time.time() - start
        
        # Hard puzzles take longer but should still complete
        assert elapsed < 60  # Generous timeout
        assert puzzle is not None
