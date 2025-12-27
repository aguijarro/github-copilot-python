"""Unit tests for sudoku_logic module."""

import pytest
from sudoku_logic import (
    create_empty_board,
    is_safe,
    fill_board,
    generate_puzzle,
    deep_copy,
    SIZE,
    EMPTY,
)


@pytest.mark.unit
class TestBoardCreation:
    """Tests for board creation functions."""

    def test_create_empty_board_dimensions(self, empty_board):
        """Test that empty board has correct dimensions."""
        assert len(empty_board) == SIZE
        assert all(len(row) == SIZE for row in empty_board)

    def test_create_empty_board_all_zeros(self, empty_board):
        """Test that all cells in empty board are zero."""
        assert all(cell == EMPTY for row in empty_board for cell in row)


@pytest.mark.unit
class TestValidation:
    """Tests for validation functions."""

    def test_is_safe_empty_position(self, empty_board):
        """Test that any number is safe in an empty board."""
        assert is_safe(empty_board, 0, 0, 1)
        assert is_safe(empty_board, 4, 4, 5)
        assert is_safe(empty_board, 8, 8, 9)

    def test_is_safe_duplicate_in_row(self, empty_board):
        """Test that duplicate in row is not safe."""
        empty_board[0][0] = 5
        assert not is_safe(empty_board, 0, 1, 5)

    def test_is_safe_duplicate_in_column(self, empty_board):
        """Test that duplicate in column is not safe."""
        empty_board[0][0] = 5
        assert not is_safe(empty_board, 1, 0, 5)

    def test_is_safe_duplicate_in_box(self, empty_board):
        """Test that duplicate in 3x3 box is not safe."""
        empty_board[0][0] = 5
        assert not is_safe(empty_board, 1, 1, 5)

    def test_is_safe_valid_position(self, empty_board):
        """Test that valid positions are recognized as safe."""
        empty_board[0][0] = 1
        empty_board[0][1] = 2
        empty_board[1][0] = 3
        assert is_safe(empty_board, 1, 1, 4)


@pytest.mark.unit
class TestDeepCopy:
    """Tests for deep copy function."""

    def test_deep_copy_creates_independent_copy(self, sample_puzzle):
        """Test that deep copy creates a completely independent board."""
        copied = deep_copy(sample_puzzle)
        copied[0][0] = 999
        assert sample_puzzle[0][0] != 999

    def test_deep_copy_preserves_values(self, sample_puzzle):
        """Test that deep copy preserves all original values."""
        copied = deep_copy(sample_puzzle)
        assert copied == sample_puzzle


@pytest.mark.unit
class TestPuzzleGeneration:
    """Tests for puzzle generation."""

    def test_generate_puzzle_returns_tuple(self):
        """Test that generate_puzzle returns both puzzle and solution."""
        result = generate_puzzle(35)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_generate_puzzle_creates_valid_dimensions(self):
        """Test that generated puzzle has correct dimensions."""
        puzzle, solution = generate_puzzle(35)
        assert len(puzzle) == SIZE
        assert len(solution) == SIZE
        assert all(len(row) == SIZE for row in puzzle)
        assert all(len(row) == SIZE for row in solution)

    def test_generate_puzzle_puzzle_is_subset_of_solution(self):
        """Test that puzzle clues are subset of the solution."""
        puzzle, solution = generate_puzzle(35)
        for i in range(SIZE):
            for j in range(SIZE):
                if puzzle[i][j] != EMPTY:
                    assert puzzle[i][j] == solution[i][j]

    def test_generate_puzzle_clue_count(self):
        """Test that generated puzzle has approximately correct clue count."""
        clues = 30
        puzzle, _ = generate_puzzle(clues)
        clue_count = sum(1 for row in puzzle for cell in row if cell != EMPTY)
        assert clue_count == clues

    @pytest.mark.slow
    def test_generate_puzzle_slow(self):
        """Test puzzle generation with fewer clues (more difficult)."""
        puzzle, solution = generate_puzzle(25)
        assert sum(1 for row in puzzle for cell in row if cell != EMPTY) == 25
