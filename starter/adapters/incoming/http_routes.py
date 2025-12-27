"""HTTP routes - inbound adapter."""

from flask import Blueprint, render_template, jsonify, request
import uuid

from domain.exceptions import SudokuError, ValidationError, GameNotFoundError
from services.game_service import GameService
from adapters.incoming.request_models import (
    NewGameRequest, CheckSolutionRequest,
    NewGameResponse, CheckSolutionResponse, ErrorResponse
)

# Will be set by app factory
game_service: GameService = None


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
    
    return bp
