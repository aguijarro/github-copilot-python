# Flask Sudoku App - Development Instructions

## Requirements

- **Python**: 3.10 or higher
- **Flask**: Latest stable version
- **Type hints**: Required for all functions and methods
- **Code style**: PEP 8 compliance

## Project Structure (Hexagonal Architecture)

```
sudoku_v2/
├── .gitignore
├── instruction.md
├── requirements.txt
├── app.py                          # Flask application entry point
├── config.py                       # Configuration management
│
├── domain/                         # Core business logic (isolated from frameworks)
│   ├── __init__.py
│   ├── sudoku_game.py             # Game rules and logic
│   └── models.py                  # Dataclasses for domain entities
│
├── ports/                         # Interface definitions (contracts)
│   ├── __init__.py
│   ├── game_repository.py         # Game storage contract
│   └── puzzle_generator.py        # Puzzle generation contract
│
├── adapters/                      # Implementations of ports
│   ├── __init__.py
│   ├── in/
│   │   ├── __init__.py
│   │   ├── routes.py              # Flask routes
│   │   └── request_dto.py         # Request/response models
│   └── out/
│       ├── __init__.py
│       ├── repository.py          # Storage implementation
│       └── generator.py           # Puzzle generation implementation
│
├── templates/                     # Flask Jinja2 templates
│   ├── base.html
│   ├── index.html
│   ├── game.html
│   └── error.html
│
├── static/                        # CSS, JavaScript, images
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── game.js
│
└── tests/                         # Unit and integration tests
    ├── __init__.py
    ├── test_sudoku_game.py
    └── test_routes.py
```

## Architecture Principles (Hexagonal/Ports & Adapters)

### 1. Domain Layer (`domain/`)
- **Purpose**: Pure business logic, independent of frameworks
- **No dependencies**: No Flask, databases, or external libraries
- **Responsibilities**: Game rules, validation, state management
- **Key file**: `sudoku_game.py` contains core Sudoku logic

### 2. Ports (`ports/`)
- **Purpose**: Define contracts/interfaces that domain needs
- **Pattern**: Abstract base classes or Protocol types
- **Examples**: GameRepository, PuzzleGenerator

### 3. Adapters (`adapters/`)
- **In-adapters** (`adapters/in/`): Handle user input (Flask routes)
- **Out-adapters** (`adapters/out/`): Implement ports (database, generation)

## Code Standards

### 1. Type Hints (Mandatory)
```python
from typing import Optional, List
from dataclasses import dataclass

@dataclass
class GameState:
    board: List[List[int]]
    difficulty: str
    moves: int = 0
```

### 2. Docstrings (Google Style)
```python
def validate_move(board: List[List[int]], row: int, col: int, num: int) -> bool:
    """Validates if a number can be placed at the given position.
    
    Args:
        board: 9x9 Sudoku board
        row: Row index (0-8)
        col: Column index (0-8)
        num: Number to validate (1-9)
    
    Returns:
        True if the move is valid, False otherwise.
    
    Raises:
        ValueError: If coordinates are out of bounds.
    """
```

### 3. PEP 8 Style
- 4 spaces for indentation
- Max line length: 88 characters
- Use f-strings for formatting: `f"Error: {error}"`
- Blank lines: 2 between top-level functions, 1 between methods

### 4. Modern Python Features
```python
# Use dataclasses instead of __init__
from dataclasses import dataclass, field

@dataclass
class Game:
    board: List[List[int]]
    difficulty: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

# Use context managers
with open('game.json') as f:
    data = json.load(f)

# Use match/case (Python 3.10+)
match difficulty:
    case "easy":
        mines = 30
    case "hard":
        mines = 70
```

### 5. Error Handling
```python
from enum import Enum

class ErrorCode(Enum):
    INVALID_MOVE = "INVALID_MOVE"
    GAME_NOT_FOUND = "GAME_NOT_FOUND"

class SudokuError(Exception):
    """Base exception for Sudoku domain."""
    def __init__(self, code: ErrorCode, message: str):
        self.code = code
        self.message = message
        super().__init__(message)

# In routes
try:
    game.place_number(row, col, num)
except SudokuError as e:
    return {"error": e.code.value, "message": e.message}, 400
```

## Development Workflow

### 1. Setup
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run Application
```bash
python app.py
```

### 3. Run Tests
```bash
pytest tests/ -v
```

### 4. Code Quality
```bash
# Format code
black . --line-length 88

# Type checking
mypy domain/ adapters/ --strict

# Lint
flake8 . --max-line-length=88
```

## Key Implementation Notes

### Domain Logic Isolation
- Game logic lives in `domain/sudoku_game.py`, not in routes
- Domain classes have zero dependencies on Flask

### Dependency Injection
```python
class GameService:
    def __init__(self, repository: GameRepository, generator: PuzzleGenerator):
        self.repository = repository
        self.generator = generator
```

### Request/Response Handling
- Input validation in `adapters/in/request_dto.py`
- Transformation between Flask and domain objects in routes
- Consistent JSON responses with status codes

### Testing Strategy
- Unit tests for domain logic (no mocks needed)
- Integration tests for adapters
- Mock external dependencies

## Resources
- [Hexagonal Architecture](https://en.wikipedia.org/wiki/Hexagonal_architecture_(software))
- [PEP 8 Style Guide](https://pep8.org/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)