# Quick Reference: Monolithic Functions & Fixes

## 🔴 CRITICAL ISSUES - FIX FIRST

### 1. Global State (Thread-Unsafe)
**File**: `starter/app.py` (Lines 8-10)
**Current Code**:
```python
CURRENT = {
    'puzzle': None,
    'solution': None
}
```
**Problem**: 
- Not thread-safe
- Multiple users interfere with each other
- Violates web application best practices

**Fix Strategy**:
- Create `GameRepository` port (interface)
- Create `MemoryGameRepository` adapter (implementation)
- Store game state keyed by session ID
- Pass repository to routes via dependency injection

**Complexity**: Medium | **Time**: 2-3 hours | **Priority**: CRITICAL

---

### 2. Recursive Puzzle Generation (Stack Overflow)
**File**: `starter/sudoku_logic.py` (Lines 14-30)
**Current Code**:
```python
def fill_board(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):  # ← RECURSIVE
                            return True
                        board[row][col] = EMPTY
                return False
    return True
```
**Problem**:
- Deep recursion (25-500+ levels)
- Stack overflow on difficult puzzles
- No timeout protection
- Hard to debug

**Fix Strategy**:
- Create explicit stack for backtracking
- Implement `get_valid_candidates(board, row, col)`
- Implement iterative `solve_cell(board, row, col)`
- Wrap in `fill_solution_board(board)`

**Complexity**: Medium | **Time**: 3-4 hours | **Priority**: CRITICAL

**Pseudo-code**:
```python
def fill_solution_board(board):
    """Fill empty board with valid solution using iterative approach."""
    stack = [(0, 0)]  # (row, col) to fill
    
    while stack:
        row, col = stack[-1]
        
        if is_filled(board, row, col):
            stack.pop()
            continue
        
        candidates = get_valid_candidates(board, row, col)
        
        if candidates:
            chosen = random.choice(candidates)
            board[row][col] = chosen
            next_pos = get_next_position(row, col)
            stack.append(next_pos)
        else:
            board[row][col] = EMPTY
            stack.pop()
    
    return board
```

---

### 3. Weak Puzzle Removal (No Uniqueness)
**File**: `starter/sudoku_logic.py` (Lines 32-38)
**Current Code**:
```python
def remove_cells(board, clues):
    attempts = SIZE * SIZE - clues
    while attempts > 0:
        row = random.randrange(SIZE)
        col = random.randrange(SIZE)
        if board[row][col] != EMPTY:
            board[row][col] = EMPTY
            attempts -= 1
```
**Problem**:
- No uniqueness check
- Puzzle may have multiple solutions
- Not a valid Sudoku puzzle
- No difficulty differentiation

**Fix Strategy**:
- Implement `verify_uniqueness(board)` function
- Track removed cells intelligently
- Verify each removal maintains unique solution
- Implement difficulty-based removal (easy/medium/hard)

**Complexity**: High | **Time**: 4-5 hours | **Priority**: CRITICAL

**Pseudo-code**:
```python
def remove_clues_for_difficulty(solution, difficulty='medium'):
    """Remove clues based on difficulty while ensuring unique solution."""
    puzzle = deep_copy(solution)
    
    # Different target clues for difficulty
    target_clues = {
        'easy': 40,
        'medium': 30,
        'hard': 20
    }[difficulty]
    
    removed = []
    
    while len(removed) < (81 - target_clues):
        row, col = random.choice([(r, c) for r in range(9) 
                                  for c in range(9) 
                                  if puzzle[r][c] != EMPTY])
        
        value = puzzle[row][col]
        puzzle[row][col] = EMPTY
        
        if has_unique_solution(puzzle):
            removed.append((row, col, value))
        else:
            puzzle[row][col] = value  # Restore
    
    return puzzle

def has_unique_solution(puzzle):
    """Check if puzzle has exactly one solution."""
    solutions = []
    
    def solve(board):
        if len(solutions) > 1:  # Early exit
            return
        
        # Find next empty cell
        for row in range(9):
            for col in range(9):
                if board[row][col] == 0:
                    for num in range(1, 10):
                        if is_safe(board, row, col, num):
                            board[row][col] = num
                            solve(board)
                            board[row][col] = 0
                    return
        
        # No empty cells - found a solution
        solutions.append(deep_copy(board))
    
    solve(deep_copy(puzzle))
    return len(solutions) == 1
```

---

## 🟡 MAJOR ISSUES - FIX SECOND

### 4. Monolithic `is_safe()` Function
**File**: `starter/sudoku_logic.py` (Lines 7-18)
**Current Code**:
```python
def is_safe(board, row, col, num):
    # Check row and column
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    # Check 3x3 box
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True
```
**Problem**:
- Violates Single Responsibility Principle
- Does 3 things: row check, column check, box check
- Hard to test individually
- Hard to reuse components

**Fix Strategy**:
Split into 4 functions:

```python
from typing import List

def is_safe_in_row(board: List[List[int]], row: int, num: int) -> bool:
    """Check if num already exists in the given row.
    
    Args:
        board: 9x9 Sudoku board (0 = empty)
        row: Row index (0-8)
        num: Number to check (1-9)
    
    Returns:
        True if num is not in row
    """
    return num not in board[row]

def is_safe_in_column(board: List[List[int]], col: int, num: int) -> bool:
    """Check if num already exists in the given column."""
    return num not in [board[row][col] for row in range(9)]

def is_safe_in_box(board: List[List[int]], row: int, col: int, num: int) -> bool:
    """Check if num already exists in the 3x3 box."""
    box_row, box_col = (row // 3) * 3, (col // 3) * 3
    for i in range(3):
        for j in range(3):
            if board[box_row + i][box_col + j] == num:
                return False
    return True

def is_safe(board: List[List[int]], row: int, col: int, num: int) -> bool:
    """Check if placing num at (row, col) is valid.
    
    Validates against Sudoku rules:
    - Row: no duplicate numbers
    - Column: no duplicate numbers
    - 3x3 Box: no duplicate numbers
    
    Args:
        board: 9x9 Sudoku board
        row: Row index (0-8)
        col: Column index (0-8)
        num: Number to place (1-9)
    
    Returns:
        True if placement is valid
    """
    return (is_safe_in_row(board, row, num) and
            is_safe_in_column(board, col, num) and
            is_safe_in_box(board, row, col, num))
```

**Complexity**: Low | **Time**: 1 hour | **Priority**: MEDIUM

---

### 5. Route Handler Complexity
**File**: `starter/app.py` (Lines 24-35)
**Current Code**:
```python
@app.route('/check', methods=['POST'])
def check_solution():
    data = request.json
    board = data.get('board')
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400
    incorrect = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if board[i][j] != solution[i][j]:
                incorrect.append([i, j])
    return jsonify({'incorrect': incorrect})
```
**Problems**:
- No input validation
- Business logic in route
- No error handling
- Direct coupling to module
- Hard to test

**Fix Strategy**:
1. Create `CheckSolutionRequest` DTO with validation
2. Create `GameService` with `check_solution()` method
3. Thin route that handles HTTP concerns only
4. Proper error responses

**Example**:
```python
# adapters/in/request_models.py
@dataclass
class CheckSolutionRequest:
    board: List[List[int]]
    
    @staticmethod
    def from_json(data: dict) -> 'CheckSolutionRequest':
        board = data.get('board')
        if not isinstance(board, list) or len(board) != 9:
            raise ValueError("Board must be 9x9 list")
        for i, row in enumerate(board):
            if not isinstance(row, list) or len(row) != 9:
                raise ValueError(f"Row {i} must have 9 elements")
            for j, cell in enumerate(row):
                if not isinstance(cell, int) or cell < 0 or cell > 9:
                    raise ValueError(f"Cell [{i}][{j}] must be 0-9")
        return CheckSolutionRequest(board=board)

# services/game_service.py
class GameService:
    def __init__(self, repo: GameRepository):
        self.repo = repo
    
    def check_solution(self, game_id: str, board: List[List[int]]) -> CheckResult:
        game = self.repo.load(game_id)
        if not game:
            raise GameNotFoundError(f"Game {game_id} not found")
        
        incorrect = []
        for i in range(9):
            for j in range(9):
                if board[i][j] != game.solution[i][j]:
                    incorrect.append((i, j))
        
        return CheckResult(
            is_correct=len(incorrect) == 0,
            incorrect_cells=incorrect
        )

# adapters/in/http_routes.py
@app.route('/check', methods=['POST'])
def check_solution(game_service: GameService):
    try:
        req = CheckSolutionRequest.from_json(request.json)
        game_id = session['game_id']
        result = game_service.check_solution(game_id, req.board)
        return jsonify({
            'is_correct': result.is_correct,
            'incorrect': result.incorrect_cells
        }), 200
    except GameNotFoundError:
        return jsonify({'error': 'Game not found'}), 404
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
```

**Complexity**: Medium | **Time**: 3-4 hours | **Priority**: MEDIUM

---

## 🟢 MINOR ISSUES - FIX THIRD

### 6. Missing Type Hints
**Impact**: Errors only caught at runtime

**Quick Fix**: Add type hints to signatures
```python
# BEFORE
def is_safe(board, row, col, num):

# AFTER
def is_safe(board: List[List[int]], row: int, col: int, num: int) -> bool:
```

**Time**: 2-3 hours | **Priority**: MEDIUM

---

### 7. Missing Docstrings
**Impact**: No function documentation

**Quick Fix**: Add Google-style docstrings
```python
def is_safe(board: List[List[int]], row: int, col: int, num: int) -> bool:
    """Check if placing num at (row, col) violates Sudoku rules.
    
    Args:
        board: 9x9 Sudoku grid (0 = empty cell)
        row: Row index (0-8)
        col: Column index (0-8)
        num: Number to validate (1-9)
    
    Returns:
        True if placement is valid, False otherwise
    
    Raises:
        ValueError: If row/col/num are out of valid range
    """
```

**Time**: 1-2 hours | **Priority**: LOW

---

### 8. Global JavaScript State
**File**: `starter/static/main.js` (Line 3)
**Current**: `let puzzle = [];`

**Fix**: Encapsulate in class or module
```javascript
const GameController = {
    puzzle: [],
    
    newGame: async function() {
        const res = await fetch('/new');
        const data = await res.json();
        this.puzzle = data.puzzle;
        this.renderBoard();
    },
    
    renderBoard: function() {
        // Use this.puzzle
    }
};
```

**Time**: 1 hour | **Priority**: LOW

---

## 📊 SUMMARY TABLE

| Issue | File | Lines | Severity | Fix Time | Dependencies |
|-------|------|-------|----------|----------|--------------|
| Global state | app.py | 8-10 | 🔴 | 2-3h | None (start here) |
| Recursive fill | sudoku_logic.py | 14-30 | 🔴 | 3-4h | Depends on #1 |
| Weak removal | sudoku_logic.py | 32-38 | 🔴 | 4-5h | Depends on #2 |
| is_safe() | sudoku_logic.py | 7-18 | 🟡 | 1h | None |
| Route handler | app.py | 24-35 | 🟡 | 3-4h | Depends on #1 |
| Type hints | All | All | 🟡 | 2-3h | None |
| Docstrings | All | All | 🟡 | 1-2h | None |
| JS globals | main.js | 3 | 🟡 | 1h | None |

---

## 🎯 RECOMMENDED IMPLEMENTATION ORDER

1. **Phase 1 - Foundation (4 hours)**
   - Fix type hints and docstrings
   - Create domain/exceptions.py
   - Create domain/models.py

2. **Phase 2 - Core Fix (6-8 hours)**
   - Fix `is_safe()` decomposition
   - Fix recursive `fill_board()`
   - Fix `remove_cells()` with uniqueness

3. **Phase 3 - Architecture (8-10 hours)**
   - Create GameRepository port
   - Create PuzzleGenerator port
   - Create adapters
   - Extract GameService

4. **Phase 4 - Integration (4-6 hours)**
   - Update routes with DI
   - Add error handling
   - Update tests

**Total Estimated Time**: 22-32 hours (3-4 working days)

---

## ✅ VERIFICATION CHECKLIST

After each fix, verify:
- [ ] All tests pass
- [ ] No new warnings
- [ ] Type hints are correct
- [ ] Docstrings are complete
- [ ] Error messages are clear
- [ ] Code is DRY (no duplication)
- [ ] Complexity metrics improved
