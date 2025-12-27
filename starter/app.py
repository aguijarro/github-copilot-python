"""Sudoku game application - Hexagonal Architecture.

Entry point for Flask application with dependency injection setup.
"""

from flask import Flask

from adapters.incoming.http_routes import create_routes_blueprint
from adapters.out.puzzle_generator import RandomPuzzleGenerator
from adapters.out.memory_repository import MemoryGameRepository
from services.game_service import GameService


def create_app(config: dict = None) -> Flask:
    """Application factory for creating Flask app with dependency injection.
    
    Args:
        config: Optional configuration dictionary
    
    Returns:
        Configured Flask application
    """
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    if config:
        app.config.update(config)
    
    # Create adapters (implementations of ports)
    puzzle_generator = RandomPuzzleGenerator()
    game_repository = MemoryGameRepository()
    
    # Create service with dependency injection
    game_service = GameService(puzzle_generator, game_repository)
    
    # Register routes with service injected
    routes_bp = create_routes_blueprint(game_service)
    app.register_blueprint(routes_bp)
    
    return app


if __name__ == '__main__':
    app = create_app({
        'DEBUG': True,
        'TESTING': False
    })
    app.run(debug=True)