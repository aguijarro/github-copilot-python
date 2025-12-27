"""Unit tests for Sudoku domain logic."""

import pytest
from domain.sudoku_game import (
    is_safe_in_row, is_safe_in_column, is_safe_in_box, is_safe,
    create_empty_board, fill_solution_board, remove_clues,
    generate_puzzle, validate_move, find_incorrect_cells,
    BOARD_SIZE, EMPTY
)
from domain.exceptions import PuzzleGenerationError, ValidationError


class TestBoardValidation:
    """Tests for board validation functions."""
    
    def test_is_safe_in_row(self, empty_board):
        """Test row validation."""
        empty_board[0][0] = 5
        assert not is_safe_in_row(empty_board, 0, 5)
        assert is_safe_in_row(empty_board, 0, 3)
    
    def test_is_safe_in_column(self, empty_board):
        """Test column validation."""
        empty_board[0][0] = 5
        assert not is_safe_in_column(empty_board, 0, 5)
        assert is_safe_in_column(empty_board, 1, 5)
    
    def test_is_safe_in_box(self, empty_board):
        """Test 3x3 box validation."""
        empty_board[0][0] = 5
        assert not is_safe_in_box(empty_board, 1, 1, 5)
        assert is_safe_in_box(empty_board, 0, 3, 5)
    
    def test_is_safe_empty_position(self, empty_board):
        """Test safety check on empty board."""
        assert is_safe(empty_board, 0, 0, 1)
        assert is_safe(empty_board, 4, 4, 5)
        assert is_safe(empty_board, 8, 8, 9)
    
    def test_is_safe_with_conflict(self, empty_board):
        """Test safety check with conflicts."""
        empty_board[0][0] = 5
        assert not is_safe(empty_board, 0, 1, 5)  # row conflict
        assert not is_safe(empty_board, 1, 0, 5)  # column conflict
        assert not is_safe(empty_board, 1, 1, 5)  # box conflict


class TestBoardCreation:
    """Tests for board creation."""
    
    def test_create_empty_board(self):
        """Test creating empty board."""
        board = create_empty_board()
        assert len(board) == BOARD_SIZE
        assert all(len(row) == BOARD_SIZE for row in board)
        assert all(cell == EMPTY for row in board for cell in row)


class TestPuzzleGeneration:
    """Tests for puzzle generation."""
    
    def test_generate_puzzle_returns_tuple(self):
        """Test puzzle generation returns correct structure."""
        puzzle, solution = generate_puzzle(35)
        assert isinstance(puzzle, list)
        assert isinstance(solution, list)
        assert len(puzzle) == BOARD_SIZE
        assert len(solution) == BOARD_SIZE
    
    def test_generate_puzzle_clue_count(self):
        """Test generated puzzle has correct clue count."""
        clues = 35
        puzzle, _ = generate_puzzle(clues)
        clue_count = sum(1 for row in puzzle for cell in row if cell != EMPTY)
        assert clue_count == clues
    
    def test_generate_puzzle_valid_clues(self):
        """Test puzzle clues are valid."""
        puzzle, solution = generate_puzzle(35)
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if puzzle[i][j] != EMPTY:
                    assert puzzle[i][j] == solution[i][j]
    
    def test_generate_puzzle_invalid_clues(self):
        """Test puzzle generation fails with invalid clue count."""
        with pytest.raises(ValueError):
            generate_puzzle(10)  # Too few
        
        with pytest.raises(ValueError):
            generate_puzzle(90)  # Too many
    
    @pytest.mark.slow
    def test_generate_puzzle_with_different_difficulties(self):
        """Test puzzle generation with different clue counts."""
        for clues in [25, 35, 45]:
            puzzle, solution = generate_puzzle(clues)
            clue_count = sum(1 for row in puzzle for cell in row if cell != EMPTY)
            assert clue_count == clues


class TestValidateMove:
    """Tests for move validation."""
    
    def test_validate_move_valid(self, empty_board):
        """Test valid move validation."""
        assert validate_move(empty_board, 0, 0, 1)
    
    def test_validate_move_invalid_position(self, empty_board):
        """Test move validation with invalid position."""
        with pytest.raises(ValueError):
            validate_move(empty_board, 10, 0, 1)
    
    def test_validate_move_invalid_number(self, empty_board):
        """Test move validation with invalid number."""
        with pytest.raises(ValueError):
            validate_move(empty_board, 0, 0, 10)
    
    def test_validate_move_cell_not_empty(self, empty_board):
        """Test move validation on non-empty cell."""
        empty_board[0][0] = 5
        with pytest.raises(ValueError):
            validate_move(empty_board, 0, 0, 1)


class TestFindIncorrectCells:
    """Tests for finding incorrect cells."""
    
    def test_find_incorrect_cells_no_errors(self, sample_solution):
        """Test finding incorrect cells when all correct."""
        current = [row[:] for row in sample_solution]
        incorrect = find_incorrect_cells(current, sample_solution)
        assert len(incorrect) == 0
    
    def test_find_incorrect_cells_with_errors(self, sample_solution):
        """Test finding incorrect cells with errors."""
        current = [row[:] for row in sample_solution]
        current[0][0] = 9  # Wrong number
        incorrect = find_incorrect_cells(current, sample_solution)
        assert (0, 0) in incorrect
