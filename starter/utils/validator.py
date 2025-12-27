"""Sudoku board validation utilities."""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

from domain.models import BOARD_SIZE, EMPTY
from domain.exceptions import ValidationError


@dataclass
class MoveValidationResult:
    """Result of validating a move.
    
    Attributes:
        is_valid: Whether the move is valid
        errors: List of error messages if invalid
        conflicts: List of (row, col) tuples showing conflicting cells
        conflict_type: Type of conflict ('row', 'column', 'box', or None)
    """
    is_valid: bool
    errors: List[str]
    conflicts: List[Tuple[int, int]] = None
    conflict_type: Optional[str] = None
    
    def __post_init__(self):
        """Initialize conflicts as empty list if None."""
        if self.conflicts is None:
            self.conflicts = []


@dataclass
class CompletionResult:
    """Result of checking board completion.
    
    Attributes:
        is_complete: Whether the board is completely filled
        empty_cells: List of (row, col) tuples for empty cells
        empty_count: Total count of empty cells
    """
    is_complete: bool
    empty_cells: List[Tuple[int, int]]
    empty_count: int


@dataclass
class ConflictInfo:
    """Information about conflicts in a board.
    
    Attributes:
        has_conflicts: Whether any conflicts exist
        row_conflicts: Dict mapping row index to list of conflicting numbers
        column_conflicts: Dict mapping column index to list of conflicting numbers
        box_conflicts: Dict mapping box index to list of conflicting numbers
        conflict_cells: List of (row, col) tuples with conflicts
        total_conflicts: Total number of conflicting cells
    """
    has_conflicts: bool
    row_conflicts: Dict[int, List[int]]
    column_conflicts: Dict[int, List[int]]
    box_conflicts: Dict[int, List[int]]
    conflict_cells: List[Tuple[int, int]]
    total_conflicts: int


class SudokuValidator:
    """Validates Sudoku board states and moves.
    
    Provides comprehensive validation with detailed error reporting for:
    - Move validation (checking if a move is legal)
    - Board completion (detecting empty cells)
    - Conflict detection (finding rule violations)
    """
    
    def __init__(self):
        """Initialize the validator."""
        pass
    
    def is_valid_move(
        self,
        board: List[List[int]],
        row: int,
        col: int,
        num: int
    ) -> MoveValidationResult:
        """Validate if a move is legal according to Sudoku rules.
        
        Checks:
        1. Position is within bounds (0-8)
        2. Number is valid (1-9)
        3. Cell is empty
        4. Number doesn't violate row rules
        5. Number doesn't violate column rules
        6. Number doesn't violate 3x3 box rules
        
        Args:
            board: 9x9 Sudoku board
            row: Row index (0-8)
            col: Column index (0-8)
            num: Number to place (1-9)
        
        Returns:
            MoveValidationResult with validation status, errors, and conflict info
        
        Examples:
            >>> validator = SudokuValidator()
            >>> board = [[0]*9 for _ in range(9)]
            >>> result = validator.is_valid_move(board, 0, 0, 5)
            >>> result.is_valid
            True
        """
        result = MoveValidationResult(is_valid=True, errors=[])
        
        # Validate position
        if not (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE):
            result.is_valid = False
            result.errors.append(f"Invalid position: ({row}, {col}). Must be within 0-8.")
            return result
        
        # Validate number
        if not (1 <= num <= BOARD_SIZE):
            result.is_valid = False
            result.errors.append(f"Invalid number: {num}. Must be between 1 and {BOARD_SIZE}.")
            return result
        
        # Check if cell is empty
        if board[row][col] != EMPTY:
            result.is_valid = False
            result.errors.append(
                f"Cell ({row}, {col}) is not empty. Contains: {board[row][col]}"
            )
            return result
        
        # Check row conflict
        if num in board[row]:
            result.is_valid = False
            result.errors.append(f"Number {num} already exists in row {row}")
            result.conflict_type = 'row'
            conflicting_col = board[row].index(num)
            result.conflicts.append((row, conflicting_col))
        
        # Check column conflict
        column = [board[r][col] for r in range(BOARD_SIZE)]
        if num in column:
            if result.is_valid:  # Only set if first error
                result.conflict_type = 'column'
            result.is_valid = False
            result.errors.append(f"Number {num} already exists in column {col}")
            conflicting_row = column.index(num)
            result.conflicts.append((conflicting_row, col))
        
        # Check 3x3 box conflict
        box_row, box_col = (row // 3) * 3, (col // 3) * 3
        box_num = (row // 3) * 3 + (col // 3)
        
        for i in range(3):
            for j in range(3):
                cell_row, cell_col = box_row + i, box_col + j
                if board[cell_row][cell_col] == num:
                    if result.is_valid:  # Only set if first error
                        result.conflict_type = 'box'
                    result.is_valid = False
                    result.errors.append(
                        f"Number {num} already exists in 3x3 box {box_num}"
                    )
                    result.conflicts.append((cell_row, cell_col))
        
        return result
    
    def check_completion(self, board: List[List[int]]) -> CompletionResult:
        """Check if the board is completely filled.
        
        Identifies all empty cells in the board.
        
        Args:
            board: 9x9 Sudoku board
        
        Returns:
            CompletionResult with completion status and empty cell list
        
        Examples:
            >>> validator = SudokuValidator()
            >>> complete_board = [[i for i in range(1, 10)] for _ in range(9)]
            >>> result = validator.check_completion(complete_board)
            >>> result.is_complete
            True
        """
        empty_cells = []
        
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if board[row][col] == EMPTY:
                    empty_cells.append((row, col))
        
        is_complete = len(empty_cells) == 0
        
        return CompletionResult(
            is_complete=is_complete,
            empty_cells=empty_cells,
            empty_count=len(empty_cells)
        )
    
    def find_conflicts(self, board: List[List[int]]) -> ConflictInfo:
        """Find all conflicts (rule violations) in the board.
        
        Detects:
        - Duplicate numbers in rows
        - Duplicate numbers in columns
        - Duplicate numbers in 3x3 boxes
        
        Args:
            board: 9x9 Sudoku board
        
        Returns:
            ConflictInfo with detailed conflict information
        
        Examples:
            >>> validator = SudokuValidator()
            >>> board = [[0]*9 for _ in range(9)]
            >>> board[0][0] = 5
            >>> board[0][1] = 5
            >>> result = validator.find_conflicts(board)
            >>> result.has_conflicts
            True
        """
        row_conflicts: Dict[int, List[int]] = {}
        column_conflicts: Dict[int, List[int]] = {}
        box_conflicts: Dict[int, List[int]] = {}
        conflict_cells: set = set()
        
        # Check rows
        for row in range(BOARD_SIZE):
            row_data = board[row]
            seen = {}
            for col in range(BOARD_SIZE):
                num = row_data[col]
                if num != EMPTY:
                    if num in seen:
                        # Found duplicate in row
                        if row not in row_conflicts:
                            row_conflicts[row] = []
                        if num not in row_conflicts[row]:
                            row_conflicts[row].append(num)
                        conflict_cells.add((row, col))
                        conflict_cells.add((row, seen[num]))
                    else:
                        seen[num] = col
        
        # Check columns
        for col in range(BOARD_SIZE):
            column_data = [board[row][col] for row in range(BOARD_SIZE)]
            seen = {}
            for row in range(BOARD_SIZE):
                num = column_data[row]
                if num != EMPTY:
                    if num in seen:
                        # Found duplicate in column
                        if col not in column_conflicts:
                            column_conflicts[col] = []
                        if num not in column_conflicts[col]:
                            column_conflicts[col].append(num)
                        conflict_cells.add((row, col))
                        conflict_cells.add((seen[num], col))
                    else:
                        seen[num] = row
        
        # Check 3x3 boxes
        for box_row in range(0, BOARD_SIZE, 3):
            for box_col in range(0, BOARD_SIZE, 3):
                box_num = (box_row // 3) * 3 + (box_col // 3)
                seen = {}
                for i in range(3):
                    for j in range(3):
                        cell_row = box_row + i
                        cell_col = box_col + j
                        num = board[cell_row][cell_col]
                        if num != EMPTY:
                            if num in seen:
                                # Found duplicate in box
                                if box_num not in box_conflicts:
                                    box_conflicts[box_num] = []
                                if num not in box_conflicts[box_num]:
                                    box_conflicts[box_num].append(num)
                                conflict_cells.add((cell_row, cell_col))
                                prev_row, prev_col = seen[num]
                                conflict_cells.add((prev_row, prev_col))
                            else:
                                seen[num] = (cell_row, cell_col)
        
        has_conflicts = len(conflict_cells) > 0
        
        return ConflictInfo(
            has_conflicts=has_conflicts,
            row_conflicts=row_conflicts,
            column_conflicts=column_conflicts,
            box_conflicts=box_conflicts,
            conflict_cells=sorted(list(conflict_cells)),
            total_conflicts=len(conflict_cells)
        )
    
    def validate_board_integrity(self, board: List[List[int]]) -> Dict:
        """Perform comprehensive board integrity check.
        
        Combines move validation, completion check, and conflict detection.
        
        Args:
            board: 9x9 Sudoku board
        
        Returns:
            Dict with comprehensive validation information:
            - is_valid: Overall validity
            - completion: CompletionResult
            - conflicts: ConflictInfo
            - summary: Human-readable summary
        """
        completion = self.check_completion(board)
        conflicts = self.find_conflicts(board)
        
        is_valid = not conflicts.has_conflicts and completion.is_complete
        
        summary_parts = []
        if conflicts.has_conflicts:
            summary_parts.append(f"{conflicts.total_conflicts} conflicting cells found")
            if conflicts.row_conflicts:
                summary_parts.append(f"Row conflicts in rows: {list(conflicts.row_conflicts.keys())}")
            if conflicts.column_conflicts:
                summary_parts.append(f"Column conflicts in columns: {list(conflicts.column_conflicts.keys())}")
            if conflicts.box_conflicts:
                summary_parts.append(f"Box conflicts in boxes: {list(conflicts.box_conflicts.keys())}")
        
        if not completion.is_complete:
            summary_parts.append(f"{completion.empty_count} empty cells")
        
        if is_valid:
            summary_parts.append("Board is valid and complete")
        
        return {
            'is_valid': is_valid,
            'completion': completion,
            'conflicts': conflicts,
            'summary': '; '.join(summary_parts) if summary_parts else "No issues found"
        }
