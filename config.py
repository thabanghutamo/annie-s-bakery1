import os
import logging
from datetime import timedelta
from pythonjsonlogger import jsonlogger
from flask_session import RedisSessionInterface


class ProductionConfig:
    # Basic Flask configuration
    DEBUG = False
    TESTING = False
    
    # Security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
    
    # Session configuration
    SESSION_TYPE = os.getenv('SESSION_TYPE', 'redis')
    PERMANENT_SESSION_LIFETIME = timedelta(seconds=int(os.getenv('PERMANENT_SESSION_LIFETIME', 2592000)))
    
    # Cache configuration
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'redis')
    CACHE_REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Upload configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = '/var/www/annies/uploads'
    
    # Rate limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Logging configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'ERROR')
    LOG_FILE = os.getenv('LOG_FILE', '/var/log/annies/application.log')
    
    @staticmethod
    def init_app(app):
        # Set up logging
        if not os.path.exists(os.path.dirname(app.config['LOG_FILE'])):
            os.makedirs(os.path.dirname(app.config['LOG_FILE']))
            
        handler = logging.FileHandler(app.config['LOG_FILE'])
        formatter = jsonlogger.JsonFormatter(
            '%(asctime)s %(levelname)s %(name)s %(message)s %(pathname)s %(lineno)s'
        )
        handler.setFormatter(formatter)
        handler.setLevel(app.config['LOG_LEVEL'])
        app.logger.addHandler(handler)
        
        # Set up session interface
        if app.config['SESSION_TYPE'] == 'redis':
            from redis import Redis
            app.session_interface = RedisSessionInterface(
                Redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0'))
            )
            
        # Set up cache
        if app.config['CACHE_TYPE'] == 'redis':
            from flask_caching import Cache
            cache = Cache(app)
            
        # Set up rate limiting
        from flask_limiter import Limiter
        from flask_limiter.util import get_remote_address
        
        limiter = Limiter(
            app=app,
            key_func=get_remote_address,
            default_limits=["200 per day", "50 per hour"],
            storage_uri=app.config['RATELIMIT_STORAGE_URL']
        )