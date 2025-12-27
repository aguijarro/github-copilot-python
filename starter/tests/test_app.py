"""Integration and unit tests for Flask routes."""

import pytest
import json
import uuid
from domain.models import EMPTY
from domain.exceptions import GameNotFoundError


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
        assert 'game_id' in data
        assert isinstance(data['puzzle'], list)

    def test_new_game_with_default_clues(self, client):
        """Test new game with default clue count."""
        response = client.get('/new')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'puzzle' in data
        assert 'game_id' in data

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

    def test_new_game_invalid_clues_too_low(self, client):
        """Test new game with too few clues."""
        response = client.get('/new?clues=5')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_new_game_invalid_clues_too_high(self, client):
        """Test new game with too many clues."""
        response = client.get('/new?clues=100')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_new_game_returns_unique_game_ids(self, client):
        """Test that multiple games get unique IDs."""
        response1 = client.get('/new?clues=35')
        data1 = json.loads(response1.data)
        
        response2 = client.get('/new?clues=35')
        data2 = json.loads(response2.data)
        
        assert data1['game_id'] != data2['game_id']


@pytest.mark.integration
class TestCheckSolutionRoute:
    """Tests for the check solution route."""

    def test_check_solution_game_not_found(self, client, sample_solution):
        """Test check solution when game doesn't exist."""
        response = client.post(
            '/check',
            data=json.dumps({
                'game_id': 'nonexistent',
                'board': sample_solution
            }),
            content_type='application/json',
        )
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data

    def test_check_solution_missing_board(self, client):
        """Test check solution with missing board parameter."""
        response = client.post(
            '/check',
            data=json.dumps({'game_id': str(uuid.uuid4())}),
            content_type='application/json',
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_check_solution_invalid_board_structure(self, client):
        """Test check solution with invalid board structure."""
        game_response = client.get('/new?clues=35')
        game_data = json.loads(game_response.data)
        game_id = game_data['game_id']
        
        response = client.post(
            '/check',
            data=json.dumps({
                'game_id': game_id,
                'board': [[1, 2, 3]]  # Invalid 3x3 board
            }),
            content_type='application/json',
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_check_solution_with_correct_board(self, client, sample_solution):
        """Test check solution with a complete valid board."""
        game_response = client.get('/new?clues=35')
        game_data = json.loads(game_response.data)
        game_id = game_data['game_id']
        
        response = client.post(
            '/check',
            data=json.dumps({
                'game_id': game_id,
                'board': sample_solution
            }),
            content_type='application/json',
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'is_correct' in data
        assert isinstance(data['is_correct'], bool)

    def test_check_solution_returns_incorrect_cells(self, client, sample_solution):
        """Test that check solution identifies incorrect cells."""
        game_response = client.get('/new?clues=35')
        game_data = json.loads(game_response.data)
        game_id = game_data['game_id']
        
        # Create a board with wrong value
        wrong_board = [row[:] for row in sample_solution]
        wrong_board[0][0] = 9
        
        response = client.post(
            '/check',
            data=json.dumps({
                'game_id': game_id,
                'board': wrong_board
            }),
            content_type='application/json',
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'is_correct' in data
        assert 'incorrect' in data


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

    def test_app_blueprint_registered(self, flask_app):
        """Test that routes blueprint is registered."""
        assert len(flask_app.blueprints) > 0
