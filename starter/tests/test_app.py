"""Integration and unit tests for Flask routes."""

import pytest
import json
from sudoku_logic import create_empty_board, EMPTY


@pytest.mark.integration
class TestFlaskRoutes:
    """Tests for Flask application routes."""

    def test_index_route_returns_200(self, client):
        """Test that index route returns status 200."""
        response = client.get('/')
        assert response.status_code == 200

    def test_index_route_returns_html(self, client):
        """Test that index route returns HTML content."""
        response = client.get('/')
        assert b'Sudoku Game' in response.data

    def test_new_game_route_returns_puzzle(self, client):
        """Test that new game route returns a puzzle."""
        response = client.get('/new?clues=35')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'puzzle' in data
        assert isinstance(data['puzzle'], list)

    def test_new_game_with_default_clues(self, client):
        """Test new game with default clue count."""
        response = client.get('/new')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'puzzle' in data

    def test_new_game_with_custom_clues(self, client):
        """Test new game with custom clue count."""
        clues = 25
        response = client.get(f'/new?clues={clues}')
        assert response.status_code == 200
        data = json.loads(response.data)
        puzzle = data['puzzle']
        clue_count = sum(1 for row in puzzle for cell in row if cell != EMPTY)
        assert clue_count == clues

    def test_new_game_puzzle_structure(self, client):
        """Test that returned puzzle has correct structure."""
        response = client.get('/new?clues=30')
        data = json.loads(response.data)
        puzzle = data['puzzle']
        assert len(puzzle) == 9
        assert all(len(row) == 9 for row in puzzle)
        assert all(isinstance(cell, int) for row in puzzle for cell in row)


@pytest.mark.integration
class TestCheckSolutionRoute:
    """Tests for the check solution route."""

    def test_check_solution_without_game_in_progress(self, client):
        """Test check solution when no game is active."""
        board = create_empty_board()
        response = client.post(
            '/check',
            data=json.dumps({'board': board}),
            content_type='application/json',
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_check_solution_with_active_game(self, client):
        """Test check solution with an active game."""
        # Start a new game first
        client.get('/new?clues=35')
        
        # Create a board (doesn't matter if correct for this test)
        board = create_empty_board()
        response = client.post(
            '/check',
            data=json.dumps({'board': board}),
            content_type='application/json',
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'incorrect' in data
        assert isinstance(data['incorrect'], list)

    def test_check_solution_returns_json(self, client):
        """Test that check solution returns valid JSON."""
        # Create a game
        client.get('/new?clues=35')
        
        board = create_empty_board()
        response = client.post(
            '/check',
            data=json.dumps({'board': board}),
            content_type='application/json',
        )
        # Should be able to parse as JSON
        data = json.loads(response.data)
        assert isinstance(data, dict)


@pytest.mark.unit
class TestFlaskConfiguration:
    """Tests for Flask app configuration."""

    def test_testing_mode_enabled(self, flask_app):
        """Test that testing mode is enabled for test client."""
        assert flask_app.config['TESTING'] is True

    def test_app_has_routes(self, flask_app):
        """Test that app has expected routes."""
        routes = [rule.rule for rule in flask_app.url_map.iter_rules()]
        assert '/' in routes
        assert '/new' in routes
        assert '/check' in routes
