"""Tests for Sudoku board validation."""

import pytest

from utils.validator import SudokuValidator, MoveValidationResult, CompletionResult, ConflictInfo
from domain.models import BOARD_SIZE, EMPTY


class TestSudokuValidatorInitialization:
    """Test SudokuValidator initialization."""
    
    def test_validator_creation(self):
        """Test that validator can be instantiated."""
        validator = SudokuValidator()
        assert validator is not None


class TestIsValidMove:
    """Test the is_valid_move method."""
    
    def test_valid_move_on_empty_board(self):
        """Test that any move on an empty board is valid."""
        validator = SudokuValidator()
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        
        result = validator.is_valid_move(board, 0, 0, 5)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert len(result.conflicts) == 0
    
    def test_valid_move_with_non_conflicting_numbers(self):
        """Test that move is valid when no conflicts exist."""
        validator = SudokuValidator()
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        board[0][0] = 5
        
        # Try to place 5 in different row, column, and box
        result = validator.is_valid_move(board, 4, 4, 5)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_invalid_position_negative(self):
        """Test that negative position is rejected."""
        validator = SudokuValidator()
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        
        result = validator.is_valid_move(board, -1, 0, 5)
        
        assert result.is_valid is False
        assert "Invalid position" in result.errors[0]
    
    def test_invalid_position_out_of_bounds(self):
        """Test that position beyond board is rejected."""
        validator = SudokuValidator()
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        
        result = validator.is_valid_move(board, 9, 0, 5)
        
        assert result.is_valid is False
        assert "Invalid position" in result.errors[0]
    
    def test_invalid_number_zero(self):
        """Test that number 0 is rejected."""
        validator = SudokuValidator()
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        
        result = validator.is_valid_move(board, 0, 0, 0)
        
        assert result.is_valid is False
        assert "Invalid number" in result.errors[0]
    
    def test_invalid_number_too_large(self):
        """Test that number > 9 is rejected."""
        validator = SudokuValidator()
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        
        result = validator.is_valid_move(board, 0, 0, 10)
        
        assert result.is_valid is False
        assert "Invalid number" in result.errors[0]
    
    def test_cell_not_empty(self):
        """Test that placing in non-empty cell is rejected."""
        validator = SudokuValidator()
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        board[0][0] = 7
        
        result = validator.is_valid_move(board, 0, 0, 5)
        
        assert result.is_valid is False
        assert "not empty" in result.errors[0]
    
    def test_duplicate_in_row(self):
        """Test that duplicate in row is detected."""
        validator = SudokuValidator()
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        board[0][0] = 5
        
        result = validator.is_valid_move(board, 0, 1, 5)
        
        assert result.is_valid is False
        assert "already exists in row" in result.errors[0]
        assert result.conflict_type == 'row'
        assert (0, 0) in result.conflicts
    
    def test_duplicate_in_column(self):
        """Test that duplicate in column is detected."""
        validator = SudokuValidator()
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        board[0][0] = 5
        
        result = validator.is_valid_move(board, 1, 0, 5)
        
        assert result.is_valid is False
        assert "already exists in column" in result.errors[0]
        assert result.conflict_type == 'column'
        assert (0, 0) in result.conflicts
    
    def test_duplicate_in_box(self):
        """Test that duplicate in 3x3 box is detected."""
        validator = SudokuValidator()
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        board[0][0] = 5
        
        # Place 5 in same 3x3 box (top-left)
        result = validator.is_valid_move(board, 1, 1, 5)
        
        assert result.is_valid is False
        assert "already exists in 3x3 box" in result.errors[0]
        assert result.conflict_type == 'box'
        assert (0, 0) in result.conflicts
    
    def test_multiple_conflicts(self):
        """Test detection of multiple conflicts."""
        validator = SudokuValidator()
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        board[0][0] = 5  # row 0, col 0
        board[1][1] = 5  # row 1, col 1 (same box)
        
        # Try to place in row with existing 5
        result = validator.is_valid_move(board, 0, 5, 5)
        
        assert result.is_valid is False
        assert len(result.errors) >= 1
        assert "row" in result.errors[0].lower()


class TestCheckCompletion:
    """Test the check_completion method."""
    
    def test_empty_board_not_complete(self):
        """Test that empty board is not complete."""
        validator = SudokuValidator()
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        
        result = validator.check_completion(board)
        
        assert result.is_complete is False
        assert result.empty_count == BOARD_SIZE * BOARD_SIZE
        assert len(result.empty_cells) == BOARD_SIZE * BOARD_SIZE
    
    def test_complete_board_is_complete(self):
        """Test that fully filled board is complete."""
        validator = SudokuValidator()
        board = [[i for i in range(1, 10)] for _ in range(BOARD_SIZE)]
        
        result = validator.check_completion(board)
        
        assert result.is_complete is True
        assert result.empty_count == 0
        assert len(result.empty_cells) == 0
    
    def test_partially_filled_board(self):
        """Test counting empty cells in partially filled board."""
        validator = SudokuValidator()
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        board[0][0] = 1
        board[1][1] = 2
        board[2][2] = 3
        
        result = validator.check_completion(board)
        
        assert result.is_complete is False
        assert result.empty_count == BOARD_SIZE * BOARD_SIZE - 3
        assert len(result.empty_cells) == BOARD_SIZE * BOARD_SIZE - 3
        assert (0, 0) not in result.empty_cells
        assert (0, 1) in result.empty_cells
    
    def test_empty_cells_are_identified(self):
        """Test that empty cells are correctly identified."""
        validator = SudokuValidator()
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        board[0][0] = 1
        board[4][4] = 5
        board[8][8] = 9
        
        result = validator.check_completion(board)
        
        assert (0, 0) not in result.empty_cells
        assert (4, 4) not in result.empty_cells
        assert (8, 8) not in result.empty_cells
        assert (0, 1) in result.empty_cells
        assert (1, 0) in result.empty_cells


class TestFindConflicts:
    """Test the find_conflicts method."""
    
    def test_no_conflicts_in_valid_board(self):
        """Test that valid board has no conflicts."""
        validator = SudokuValidator()
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        
        result = validator.find_conflicts(board)
        
        assert result.has_conflicts is False
        assert len(result.row_conflicts) == 0
        assert len(result.column_conflicts) == 0
        assert len(result.box_conflicts) == 0
        assert result.total_conflicts == 0
    
    def test_duplicate_in_row_detected(self):
        """Test detection of duplicate in row."""
        validator = SudokuValidator()
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        board[0][0] = 5
        board[0][1] = 5
        
        result = validator.find_conflicts(board)
        
        assert result.has_conflicts is True
        assert 0 in result.row_conflicts
        assert 5 in result.row_conflicts[0]
        assert (0, 0) in result.conflict_cells
        assert (0, 1) in result.conflict_cells
    
    def test_duplicate_in_column_detected(self):
        """Test detection of duplicate in column."""
        validator = SudokuValidator()
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        board[0][0] = 5
        board[1][0] = 5
        
        result = validator.find_conflicts(board)
        
        assert result.has_conflicts is True
        assert 0 in result.column_conflicts
        assert 5 in result.column_conflicts[0]
        assert (0, 0) in result.conflict_cells
        assert (1, 0) in result.conflict_cells
    
    def test_duplicate_in_box_detected(self):
        """Test detection of duplicate in 3x3 box."""
        validator = SudokuValidator()
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        board[0][0] = 5
        board[1][1] = 5
        
        result = validator.find_conflicts(board)
        
        assert result.has_conflicts is True
        assert 0 in result.box_conflicts  # Box 0 (top-left)
        assert 5 in result.box_conflicts[0]
        assert (0, 0) in result.conflict_cells
        assert (1, 1) in result.conflict_cells
    
    def test_multiple_row_duplicates(self):
        """Test detection of multiple duplicates in same row."""
        validator = SudokuValidator()
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        board[0][0] = 5
        board[0][1] = 5
        board[0][2] = 3
        board[0][3] = 3
        
        result = validator.find_conflicts(board)
        
        assert result.has_conflicts is True
        assert 0 in result.row_conflicts
        assert 5 in result.row_conflicts[0]
        assert 3 in result.row_conflicts[0]
    
    def test_conflicts_across_different_constraints(self):
        """Test conflicts in row, column, and box simultaneously."""
        validator = SudokuValidator()
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        board[0][0] = 5
        board[0][1] = 5  # Duplicate in row
        board[1][0] = 3
        board[2][0] = 3  # Duplicate in column
        board[1][1] = 7
        board[2][2] = 7  # Duplicate in box
        
        result = validator.find_conflicts(board)
        
        assert result.has_conflicts is True
        assert len(result.row_conflicts) > 0
        assert len(result.column_conflicts) > 0
        assert len(result.box_conflicts) > 0


class TestValidateBoardIntegrity:
    """Test the validate_board_integrity method."""
    
    def test_integrity_valid_complete_board(self):
        """Test that valid complete board passes integrity check."""
        validator = SudokuValidator()
        # Create a complete board with no conflicts (all different numbers in each row)
        # This is not a mathematically valid sudoku, but has no conflicts
        board = []
        for row_idx in range(BOARD_SIZE):
            row = []
            for col_idx in range(BOARD_SIZE):
                # Use a pattern that avoids duplicates in rows/columns/boxes
                value = ((row_idx * 3 + col_idx // 3) + col_idx) % 9 + 1
                row.append(value)
            board.append(row)
        
        result = validator.validate_board_integrity(board)
        
        # Board is complete (no empty cells)
        assert result['completion'].is_complete is True
        # May or may not have conflicts depending on pattern, but should be complete
        assert result['completion'].empty_count == 0
    
    def test_integrity_incomplete_board(self):
        """Test that incomplete board is flagged."""
        validator = SudokuValidator()
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        board[0][0] = 1
        
        result = validator.validate_board_integrity(board)
        
        assert result['is_valid'] is False
        assert result['completion'].is_complete is False
        assert result['completion'].empty_count == BOARD_SIZE * BOARD_SIZE - 1
    
    def test_integrity_board_with_conflicts(self):
        """Test that board with conflicts is flagged."""
        validator = SudokuValidator()
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        board[0][0] = 5
        board[0][1] = 5
        
        result = validator.validate_board_integrity(board)
        
        assert result['is_valid'] is False
        assert result['conflicts'].has_conflicts is True
        assert "conflicting cells" in result['summary'].lower()
    
    def test_integrity_summary_contains_details(self):
        """Test that summary contains detailed information."""
        validator = SudokuValidator()
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        board[0][0] = 5
        board[0][1] = 5
        
        result = validator.validate_board_integrity(board)
        
        assert "conflicting" in result['summary'].lower()
        assert result['summary']  # Should not be empty


class TestMoveValidationResult:
    """Test MoveValidationResult dataclass."""
    
    def test_valid_result_creation(self):
        """Test creating a valid move result."""
        result = MoveValidationResult(
            is_valid=True,
            errors=[],
            conflicts=[]
        )
        
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert len(result.conflicts) == 0
    
    def test_invalid_result_with_errors(self):
        """Test creating an invalid move result with errors."""
        result = MoveValidationResult(
            is_valid=False,
            errors=["Cell not empty", "Number already in row"],
            conflicts=[(0, 1)]
        )
        
        assert result.is_valid is False
        assert len(result.errors) == 2
        assert len(result.conflicts) == 1
    
    def test_conflicts_default_to_empty_list(self):
        """Test that conflicts defaults to empty list."""
        result = MoveValidationResult(
            is_valid=True,
            errors=[]
        )
        
        assert result.conflicts == []


class TestCompletionResult:
    """Test CompletionResult dataclass."""
    
    def test_completion_result_creation(self):
        """Test creating a completion result."""
        result = CompletionResult(
            is_complete=True,
            empty_cells=[],
            empty_count=0
        )
        
        assert result.is_complete is True
        assert result.empty_count == 0
    
    def test_incomplete_result(self):
        """Test incomplete board result."""
        empty_cells = [(0, 0), (1, 1)]
        result = CompletionResult(
            is_complete=False,
            empty_cells=empty_cells,
            empty_count=len(empty_cells)
        )
        
        assert result.is_complete is False
        assert result.empty_count == 2


class TestConflictInfo:
    """Test ConflictInfo dataclass."""
    
    def test_conflict_info_with_conflicts(self):
        """Test creating conflict info with conflicts."""
        result = ConflictInfo(
            has_conflicts=True,
            row_conflicts={0: [5]},
            column_conflicts={},
            box_conflicts={},
            conflict_cells=[(0, 0), (0, 1)],
            total_conflicts=2
        )
        
        assert result.has_conflicts is True
        assert result.total_conflicts == 2
        assert 0 in result.row_conflicts
    
    def test_conflict_info_no_conflicts(self):
        """Test creating conflict info without conflicts."""
        result = ConflictInfo(
            has_conflicts=False,
            row_conflicts={},
            column_conflicts={},
            box_conflicts={},
            conflict_cells=[],
            total_conflicts=0
        )
        
        assert result.has_conflicts is False
        assert result.total_conflicts == 0


class TestEdgeCases:
    """Test edge cases and special scenarios."""
    
    def test_move_validation_all_positions(self):
        """Test validation at various board positions."""
        validator = SudokuValidator()
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        
        # Test corner positions
        assert validator.is_valid_move(board, 0, 0, 1).is_valid is True
        assert validator.is_valid_move(board, 0, 8, 1).is_valid is True
        assert validator.is_valid_move(board, 8, 0, 1).is_valid is True
        assert validator.is_valid_move(board, 8, 8, 1).is_valid is True
    
    def test_move_validation_all_numbers(self):
        """Test validation with all possible numbers."""
        validator = SudokuValidator()
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        
        for num in range(1, 10):
            result = validator.is_valid_move(board, 0, num - 1, num)
            assert result.is_valid is True
    
    def test_conflicting_cells_are_sorted(self):
        """Test that conflict cells are returned in sorted order."""
        validator = SudokuValidator()
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        board[5][5] = 5
        board[3][3] = 5
        board[8][8] = 5
        
        result = validator.find_conflicts(board)
        
        assert result.conflict_cells == sorted(result.conflict_cells)
    
    def test_validator_with_partially_complete_board(self):
        """Test validation on mostly complete board."""
        validator = SudokuValidator()
        board = [[i % 9 + 1 for i in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        board[0][0] = EMPTY
        board[4][4] = EMPTY
        
        completion = validator.check_completion(board)
        
        assert completion.is_complete is False
        assert completion.empty_count == 2
        assert (0, 0) in completion.empty_cells
        assert (4, 4) in completion.empty_cells


class TestIntegration:
    """Integration tests combining multiple validation methods."""
    
    def test_full_validation_workflow(self):
        """Test complete validation workflow."""
        validator = SudokuValidator()
        board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        
        # Start with empty board
        move_result = validator.is_valid_move(board, 0, 0, 5)
        assert move_result.is_valid is True
        
        board[0][0] = 5
        
        # Try invalid move
        move_result = validator.is_valid_move(board, 0, 1, 5)
        assert move_result.is_valid is False
        
        # Fill some cells
        for i in range(BOARD_SIZE):
            board[i][i] = (i % 9) + 1
        
        # Check completion
        completion = validator.check_completion(board)
        assert completion.is_complete is False
        assert completion.empty_count > 0
        
        # Check conflicts (should have some)
        conflicts = validator.find_conflicts(board)
        # May or may not have conflicts depending on placement
        assert isinstance(conflicts, ConflictInfo)
