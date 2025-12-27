"""Application configuration."""

import os


class Config:
    """Base configuration."""
    
    DEBUG = False
    TESTING = False
    BOARD_SIZE = 9
    EMPTY_CELL = 0


class DevelopmentConfig(Config):
    """Development configuration."""
    
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Testing configuration."""
    
    TESTING = True
    DEBUG = False


class ProductionConfig(Config):
    """Production configuration."""
    
    DEBUG = False
    TESTING = False


def get_config(env: str = None) -> Config:
    """Get configuration based on environment.
    
    Args:
        env: Environment name (development, testing, production)
    
    Returns:
        Configuration object
    """
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')
    
    config_map = {
        'development': DevelopmentConfig,
        'testing': TestingConfig,
        'production': ProductionConfig,
    }
    
    return config_map.get(env, DevelopmentConfig)()
