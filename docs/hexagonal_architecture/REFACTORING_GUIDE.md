# Hexagonal Architecture Refactoring Implementation Guide

## Quick Summary of Monolithic Functions

### 🔴 CRITICAL ISSUES

1. **Global State in `app.py`** (Lines 8-10)
   ```python
   CURRENT = {'puzzle': None, 'solution': None}  # ❌ Thread-unsafe
   ```
   - **Problem**: Multiple concurrent users will interfere
   - **Impact**: High - breaks in production
   - **Fix**: Use session-scoped storage via ports/adapters

2. **Recursive `fill_board()` in `sudoku_logic.py`** (Lines 14-30)
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
                           if fill_board(board):  # ❌ Deep recursion
                               return True
                           board[row][col] = EMPTY
                   return False
       return True
   ```
   - **Problem**: 
     - Unbounded recursion depth
     - Stack overflow risk on large grids
     - No timeout protection
     - Hard to test and debug
   - **Fix**: Convert to iterative with explicit stack
   - **Impact**: High - can crash the application

3. **Weak `remove_cells()` in `sudoku_logic.py`** (Lines 32-38)
   ```python
   def remove_cells(board, clues):
       attempts = SIZE * SIZE - clues
       while attempts > 0:
           row = random.randrange(SIZE)
           col = random.randrange(SIZE)
           if board[row][col] != EMPTY:
               board[row][col] = EMPTY
               attempts -= 1  # ❌ No uniqueness check
   ```
   - **Problem**:
     - No guarantee puzzle has unique solution
     - Can loop forever if attempts >= clues
     - May create unsolvable puzzles
     - No difficulty-based removal strategy
   - **Fix**: Add uniqueness verification and smart removal
   - **Impact**: Medium - poor puzzle quality

4. **Complex `is_safe()` in `sudoku_logic.py`** (Lines 7-18)
   ```python
   def is_safe(board, row, col, num):  # ❌ Too many concerns
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
   - **Problem**:
     - Does 3 things at once (row, col, box validation)
     - Hard to test individual components
     - Unclear variable names
   - **Fix**: Split into 3 focused functions
   - **Impact**: Low-Medium - affects code quality

5. **Route Complexity in `app.py`** (Lines 24-35)
   ```python
   @app.route('/check', methods=['POST'])
   def check_solution():  # ❌ Mixed concerns
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
   - **Problem**:
     - Direct business logic in route
     - No input validation
     - No DTO pattern
     - No error handling for malformed input
     - Tightly coupled to sudoku_logic module
   - **Fix**: Extract to service layer with DTOs
   - **Impact**: Medium - affects maintainability

### 🟡 MEDIUM ISSUES

6. **Frontend State Management in `main.js`** (Line 3)
   ```javascript
   let puzzle = [];  // ❌ Global mutable state
   ```
   - **Problem**: Multiple game instances would conflict
   - **Fix**: Encapsulate in class or use modules
   - **Impact**: Medium - affects code organization

7. **Mixed Rendering Logic in `renderPuzzle()`** (Lines 28-45)
   - **Problem**: Creates DOM, manages state, applies styles all at once
   - **Fix**: Separate concerns into controller, model, view
   - **Impact**: Low-Medium - affects maintainability

### 🟢 LOW ISSUES

8. **Missing Type Hints Everywhere**
   - **Impact**: Low - but improves IDE support and prevents runtime errors

9. **No Configuration Management**
   - **Impact**: Low - but reduces flexibility

10. **Incomplete Error Handling**
    - **Impact**: Low - poor UX on errors

---

## Refactoring Strategy by Priority

### Priority 1: Fix Thread-Safety (CRITICAL)
1. Create GameRepository port
2. Implement MemoryGameRepository adapter
3. Update routes to inject repository
4. Remove global CURRENT dict

### Priority 2: Fix Puzzle Generation (HIGH)
1. Create domain models (Board, Game)
2. Create PuzzleGenerator port
3. Refactor sudoku_logic into domain layer
4. Implement RandomPuzzleGenerator adapter
5. Add uniqueness checking

### Priority 3: Add Type Safety & Error Handling (MEDIUM)
1. Add type hints to all functions
2. Create domain exceptions
3. Add request validation DTOs
4. Update routes for error handling

### Priority 4: Improve Code Organization (MEDIUM)
1. Implement service/use-case layer
2. Create request/response models
3. Add comprehensive docstrings
4. Refactor JavaScript into modules

### Priority 5: Configuration & Documentation (LOW)
1. Add config.py
2. Add configuration to app initialization
3. Complete API documentation

---

## Code Structure Comparison

### BEFORE: Monolithic
```
app.py
  └─ Global state (CURRENT)
  └─ Routes (HTTP handlers)
     └─ Direct calls to sudoku_logic

sudoku_logic.py
  └─ Complex is_safe()
  └─ Recursive fill_board()
  └─ Weak remove_cells()
  └─ generate_puzzle() (orchestrates above)

main.js
  └─ Global puzzle state
  └─ Mixed rendering/validation/API calls
```

### AFTER: Hexagonal Architecture
```
app.py
  └─ Application factory
  └─ Dependency injection setup

domain/
  ├─ models.py (data structures)
  ├─ sudoku_game.py (pure logic)
  └─ exceptions.py (custom errors)

ports/
  ├─ puzzle_generator.py (interface)
  └─ game_repository.py (interface)

adapters/
  ├─ in/
  │  ├─ http_routes.py (HTTP handlers)
  │  └─ request_models.py (DTOs)
  └─ out/
     ├─ puzzle_generator.py (implementation)
     └─ memory_repository.py (implementation)

services/
  └─ game_service.py (use cases)

static/js/
  ├─ game.js (controller)
  ├─ board.js (view)
  └─ api.js (API client)
```

---

## Function Decomposition Examples

### Example 1: `is_safe()` → 3 Functions

```python
# BEFORE (20 lines, 3 concerns)
def is_safe(board, row, col, num):
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

# AFTER (4 focused functions)
def is_safe_in_row(board: List[List[int]], row: int, num: int) -> bool:
    """Check if num exists in row."""
    return num not in board[row]

def is_safe_in_column(board: List[List[int]], col: int, num: int) -> bool:
    """Check if num exists in column."""
    return num not in [board[row][col] for row in range(SIZE)]

def is_safe_in_box(board: List[List[int]], row: int, col: int, num: int) -> bool:
    """Check if num exists in 3x3 box."""
    box_row, box_col = (row // 3) * 3, (col // 3) * 3
    for i in range(3):
        for j in range(3):
            if board[box_row + i][box_col + j] == num:
                return False
    return True

def is_safe(board: List[List[int]], row: int, col: int, num: int) -> bool:
    """Check if placing num at (row, col) is valid."""
    return (is_safe_in_row(board, row, num) and
            is_safe_in_column(board, col, num) and
            is_safe_in_box(board, row, col, num))
```

**Benefits**:
- Easier to test each rule separately
- Reusable functions
- Clear responsibility
- Easier to debug

### Example 2: `check_solution()` Route → Service

```python
# BEFORE (monolithic route)
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

# AFTER (separated concerns)

# Domain: CheckResult (value object)
@dataclass
class CheckResult:
    is_correct: bool
    incorrect_cells: List[Tuple[int, int]]

# Service: GameService (use case)
class GameService:
    def __init__(self, repo: GameRepository):
        self.repo = repo
    
    def check_solution(self, game_id: str, board: List[List[int]]) -> CheckResult:
        game_state = self.repo.load(game_id)
        if not game_state:
            raise GameNotFoundError(game_id)
        
        incorrect = []
        for i in range(SIZE):
            for j in range(SIZE):
                if board[i][j] != game_state.solution[i][j]:
                    incorrect.append((i, j))
        
        return CheckResult(
            is_correct=len(incorrect) == 0,
            incorrect_cells=incorrect
        )

# DTO: CheckSolutionRequest (input validation)
@dataclass
class CheckSolutionRequest:
    board: List[List[int]]
    
    @staticmethod
    def from_json(data: dict) -> 'CheckSolutionRequest':
        board = data.get('board')
        if not isinstance(board, list) or len(board) != 9:
            raise ValueError("Invalid board format")
        return CheckSolutionRequest(board=board)

# Route: HTTP handler (thin wrapper)
@app.route('/check', methods=['POST'])
def check_solution():
    try:
        req = CheckSolutionRequest.from_json(request.json)
        result = game_service.check_solution(get_game_id(), req.board)
        return jsonify({
            'is_correct': result.is_correct,
            'incorrect_cells': result.incorrect_cells
        })
    except GameNotFoundError:
        return jsonify({'error': 'Game not found'}), 404
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
```

**Benefits**:
- Service layer testable without Flask
- Input validation with DTOs
- Error handling with custom exceptions
- Reusable service (could be called from CLI, scheduler, etc.)
- Routes are thin and maintainable

---

## Key Metrics for Success

| Metric | Before | Target |
|--------|--------|--------|
| **Type Hint Coverage** | 0% | 100% |
| **Cyclomatic Complexity** | High | < 5 per function |
| **Test Coverage** | ~70% | > 85% |
| **Global Mutable State** | 2 | 0 |
| **Monolithic Functions** | 5 | 0 |
| **Docstring Coverage** | 0% | 100% |
| **Dependency Injection** | None | All routes |
| **Number of Abstractions** | 0 | 4+ (ports) |

---

## Next Steps

1. **Review** this analysis with the team
2. **Create** `domain/` package with models
3. **Create** `ports/` package with interfaces
4. **Create** `adapters/` package with implementations
5. **Migrate** code incrementally (test-driven)
6. **Update** tests to use mocks and fixtures
7. **Document** API using OpenAPI/Swagger
8. **Performance** test puzzle generation
