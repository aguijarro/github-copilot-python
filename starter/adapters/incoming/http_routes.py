"""HTTP routes - inbound adapter."""

from flask import Blueprint, render_template, jsonify, request
import uuid

from domain.exceptions import SudokuError, ValidationError, GameNotFoundError
from services.game_service import GameService
from adapters.incoming.request_models import (
    NewGameRequest, CheckSolutionRequest,
    NewGameResponse, CheckSolutionResponse, ErrorResponse
)
from utils.validator import SudokuValidator

# Will be set by app factory
game_service: GameService = None
validator = SudokuValidator()


def create_routes_blueprint(service: GameService) -> Blueprint:
    """Create and configure routes blueprint.
    
    Args:
        service: GameService instance for dependency injection
    
    Returns:
        Configured Flask Blueprint
    """
    global game_service
    game_service = service
    
    bp = Blueprint('sudoku', __name__)
    
    @bp.route('/')
    def index():
        """Serve the main game page."""
        return render_template('index.html')
    
    @bp.route('/new')
    def new_game():
        """Start a new game.
        
        Query parameters:
            difficulty: Difficulty level (easy, medium, hard - default medium)
            clues: Number of visible clues (17-81, overrides difficulty if set)
        
        Returns:
            JSON with puzzle and game_id
        """
        try:
            clues_arg = request.args.get('clues')
            difficulty_arg = request.args.get('difficulty')
            req = NewGameRequest.from_args(clues_arg, difficulty_arg)
            game_id = str(uuid.uuid4())
            puzzle = game_service.start_new_game(game_id, req.clues)
            
            response = NewGameResponse(puzzle=puzzle, game_id=game_id)
            return jsonify(response.to_dict()), 200
        
        except ValidationError as e:
            error = ErrorResponse(error=str(e), code='VALIDATION_ERROR')
            return jsonify(error.to_dict()), 400
        
        except SudokuError as e:
            error = ErrorResponse(error=str(e), code='SUDOKU_ERROR')
            return jsonify(error.to_dict()), 500
        
        except Exception as e:
            error = ErrorResponse(error='Internal server error', code='SERVER_ERROR')
            return jsonify(error.to_dict()), 500
    
    @bp.route('/check', methods=['POST'])
    def check_solution():
        """Check if solution is correct.
        
        Request body:
            {
                "board": 9x9 2D array of integers (0-9),
                "game_id": optional game identifier
            }
        
        Returns:
            JSON with check result
        """
        try:
            data = request.get_json()
            if not data:
                raise ValidationError("Request body must be valid JSON")
            
            req = CheckSolutionRequest.from_json(data)
            
            # Get game_id from request or session/context
            game_id = data.get('game_id', 'default')
            
            result = game_service.check_solution(game_id, req.board)
            
            response = CheckSolutionResponse(
                is_correct=result.is_correct,
                incorrect_cells=[[r, c] for r, c in result.incorrect_cells],
                message="Correct!" if result.is_correct else "Some cells are incorrect"
            )
            return jsonify(response.to_dict()), 200
        
        except ValidationError as e:
            error = ErrorResponse(error=str(e), code='VALIDATION_ERROR')
            return jsonify(error.to_dict()), 400
        
        except GameNotFoundError as e:
            error = ErrorResponse(error=str(e), code='GAME_NOT_FOUND')
            return jsonify(error.to_dict()), 404
        
        except SudokuError as e:
            error = ErrorResponse(error=str(e), code='SUDOKU_ERROR')
            return jsonify(error.to_dict()), 500
        
        except Exception as e:
            error = ErrorResponse(error='Internal server error', code='SERVER_ERROR')
            return jsonify(error.to_dict()), 500
    
    @bp.route('/validate', methods=['POST'])
    def validate_board():
        """Validate a board and return conflicts.
        
        Request body:
            {
                "board": 9x9 2D array of integers (0-9)
            }
        
        Returns:
            JSON with conflict information:
            {
                "has_conflicts": boolean,
                "conflicts": list of [row, col] positions with conflicts,
                "row_conflicts": dict of row index to list of conflicting numbers,
                "column_conflicts": dict of column index to list of conflicting numbers,
                "box_conflicts": dict of box index to list of conflicting numbers,
                "total_conflicts": count of conflicting cells
            }
        """
        try:
            data = request.get_json()
            if not data:
                raise ValidationError("Request body must be valid JSON")
            
            board = data.get('board')
            if board is None:
                raise ValidationError("Missing 'board' field")
            
            # Validate board structure
            if not isinstance(board, list):
                raise ValidationError("Board must be a list")
            
            if len(board) != 9:
                raise ValidationError("Board must have 9 rows")
            
            for i, row in enumerate(board):
                if not isinstance(row, list):
                    raise ValidationError(f"Row {i} must be a list")
                if len(row) != 9:
                    raise ValidationError(f"Row {i} must have 9 columns")
                for j, cell in enumerate(row):
                    if not isinstance(cell, int):
                        raise ValidationError(f"Cell [{i}][{j}] must be an integer")
                    if not (0 <= cell <= 9):
                        raise ValidationError(f"Cell [{i}][{j}] must be between 0 and 9")
            
            # Find conflicts using validator
            conflict_info = validator.find_conflicts(board)
            
            return jsonify({
                'has_conflicts': conflict_info.has_conflicts,
                'conflicts': [[r, c] for r, c in conflict_info.conflict_cells],
                'row_conflicts': conflict_info.row_conflicts,
                'column_conflicts': conflict_info.column_conflicts,
                'box_conflicts': conflict_info.box_conflicts,
                'total_conflicts': conflict_info.total_conflicts
            }), 200
        
        except ValidationError as e:
            error = ErrorResponse(error=str(e), code='VALIDATION_ERROR')
            return jsonify(error.to_dict()), 400
        
        except Exception as e:
            error = ErrorResponse(error='Internal server error', code='SERVER_ERROR')
            return jsonify(error.to_dict()), 500
    
    @bp.route('/check-complete', methods=['POST'])
    def check_complete():
        """Check if board is completely filled.
        
        Request body:
            {
                "board": 9x9 2D array of integers (0-9)
            }
        
        Returns:
            JSON with completion status:
            {
                "is_complete": boolean,
                "empty_count": number of empty cells,
                "message": status message
            }
        """
        try:
            data = request.get_json()
            if not data:
                raise ValidationError("Request body must be valid JSON")
            
            board = data.get('board')
            if board is None:
                raise ValidationError("Missing 'board' field")
            
            # Validate board structure
            if not isinstance(board, list):
                raise ValidationError("Board must be a list")
            
            if len(board) != 9:
                raise ValidationError("Board must have 9 rows")
            
            for i, row in enumerate(board):
                if not isinstance(row, list):
                    raise ValidationError(f"Row {i} must be a list")
                if len(row) != 9:
                    raise ValidationError(f"Row {i} must have 9 columns")
                for j, cell in enumerate(row):
                    if not isinstance(cell, int):
                        raise ValidationError(f"Cell [{i}][{j}] must be an integer")
                    if not (0 <= cell <= 9):
                        raise ValidationError(f"Cell [{i}][{j}] must be between 0 and 9")
            
            # Check board completion using validator
            completion_result = validator.check_completion(board)
            
            message = ""
            if completion_result.is_complete:
                message = "Board is complete!"
            else:
                message = f"{completion_result.empty_count} cells remaining"
            
            return jsonify({
                'is_complete': completion_result.is_complete,
                'empty_count': completion_result.empty_count,
                'message': message
            }), 200
        
        except ValidationError as e:
            error = ErrorResponse(error=str(e), code='VALIDATION_ERROR')
            return jsonify(error.to_dict()), 400
        
        except Exception as e:
            error = ErrorResponse(error='Internal server error', code='SERVER_ERROR')
            return jsonify(error.to_dict()), 500
    
    @bp.route('/hint', methods=['POST'])
    def get_hint():
        """Get a hint by filling a random empty cell.
        
        Request body:
            {
                "board": 9x9 2D array of integers (0-9),
                "game_id": optional game identifier
            }
        
        Returns:
            JSON with hint info:
            {
                "row": cell row index,
                "col": cell column index,
                "value": correct value for the cell,
                "hints_used": total hints used so far
            }
        """
        try:
            data = request.get_json()
            if not data:
                raise ValidationError("Request body must be valid JSON")
            
            board = data.get('board')
            if board is None:
                raise ValidationError("Missing 'board' field")
            
            # Validate board structure
            if not isinstance(board, list):
                raise ValidationError("Board must be a list")
            
            if len(board) != 9:
                raise ValidationError("Board must have 9 rows")
            
            for i, row in enumerate(board):
                if not isinstance(row, list):
                    raise ValidationError(f"Row {i} must be a list")
                if len(row) != 9:
                    raise ValidationError(f"Row {i} must have 9 columns")
                for j, cell in enumerate(row):
                    if not isinstance(cell, int):
                        raise ValidationError(f"Cell [{i}][{j}] must be an integer")
                    if not (0 <= cell <= 9):
                        raise ValidationError(f"Cell [{i}][{j}] must be between 0 and 9")
            
            # Get game_id from request
            game_id = data.get('game_id', 'default')
            
            # Get hint from service
            hint_info = game_service.get_hint(game_id, board)
            
            return jsonify({
                'row': hint_info['row'],
                'col': hint_info['col'],
                'value': hint_info['value'],
                'hints_used': hint_info['hints_used']
            }), 200
        
        except ValidationError as e:
            error = ErrorResponse(error=str(e), code='VALIDATION_ERROR')
            return jsonify(error.to_dict()), 400
        
        except GameNotFoundError as e:
            error = ErrorResponse(error=str(e), code='GAME_NOT_FOUND')
            return jsonify(error.to_dict()), 404
        
        except Exception as e:
            error = ErrorResponse(error='Internal server error', code='SERVER_ERROR')
            return jsonify(error.to_dict()), 500
    
    @bp.route('/api/scores', methods=['GET'])
    def get_scores():
        """Get all scores from the scoreboard (localStorage).
        
        Returns:
            JSON list of scores sorted by time (fastest first)
        """
        try:
            from models.scoreboard import Scoreboard
            scoreboard = Scoreboard()
            scores = scoreboard.get_top_10()
            
            # Convert Score objects to dictionaries
            scores_data = [score.to_dict() for score in scores]
            
            return jsonify(scores_data), 200
        
        except FileNotFoundError:
            # No scores file yet
            return jsonify([]), 200
        
        except Exception as e:
            error = ErrorResponse(error='Failed to load scores', code='SCORES_ERROR')
            return jsonify(error.to_dict()), 500
    
    @bp.route('/api/scores', methods=['POST'])
    def save_score():
        """Save a new score to the scoreboard.
        
        Expected JSON body:
        {
            "name": "Player Name",
            "time": 300,
            "difficulty": "medium",
            "hints": 2
        }
        
        Returns:
            JSON with saved score or error
        """
        try:
            from models.scoreboard import Scoreboard
            
            data = request.get_json()
            
            if not data:
                error = ErrorResponse(error='Request body must be JSON', code='INVALID_REQUEST')
                return jsonify(error.to_dict()), 400
            
            # Extract and validate fields
            name = data.get('name', '').strip()
            time = data.get('time')
            difficulty = data.get('difficulty', '').lower()
            hints = data.get('hints')
            
            # Validate name
            if not name or len(name) < 1 or len(name) > 20:
                error = ErrorResponse(
                    error='Name must be 1-20 characters',
                    code='INVALID_NAME'
                )
                return jsonify(error.to_dict()), 400
            
            # Validate time
            if time is None or not isinstance(time, (int, float)) or time < 0:
                error = ErrorResponse(
                    error='Time must be a non-negative number',
                    code='INVALID_TIME'
                )
                return jsonify(error.to_dict()), 400
            
            # Validate difficulty
            if difficulty not in ('easy', 'medium', 'hard', 'expert'):
                error = ErrorResponse(
                    error='Invalid difficulty level',
                    code='INVALID_DIFFICULTY'
                )
                return jsonify(error.to_dict()), 400
            
            # Validate hints
            if hints is None or not isinstance(hints, int) or hints < 0:
                error = ErrorResponse(
                    error='Hints must be a non-negative integer',
                    code='INVALID_HINTS'
                )
                return jsonify(error.to_dict()), 400
            
            # Save score
            scoreboard = Scoreboard()
            score = scoreboard.add_score(
                name=name,
                time=int(time),
                difficulty=difficulty,
                hints=hints
            )
            
            return jsonify(score.to_dict()), 201
        
        except ValueError as e:
            error = ErrorResponse(error=str(e), code='VALIDATION_ERROR')
            return jsonify(error.to_dict()), 400
        
        except Exception as e:
            error = ErrorResponse(error='Failed to save score', code='SERVER_ERROR')
            return jsonify(error.to_dict()), 500
    
    return bp
