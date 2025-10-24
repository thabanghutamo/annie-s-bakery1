import os
import threading
import time
from datetime import datetime
from typing import Optional, Dict, Any, List

import secrets
from flask import Flask, request, session
from flask_login import LoginManager
from dotenv import load_dotenv

from models.user import User
from routes.admin_routes import bp as admin_bp
from routes.auth_routes import bp as auth_bp
from routes.order_routes import orders_bp
from routes.public_routes import bp as public_bp
from utils.json_store import read_json, write_json
from utils.files import init_upload_dirs

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# CSRF Protection
@app.before_request
def csrf_protect():
    if request.method == "POST":
        token = session.get('_csrf_token', None)
        if not token or token != request.form.get('_csrf_token'):
            return 'Invalid CSRF token', 400

def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = secrets.token_hex(16)
    return session['_csrf_token']

app.jinja_env.globals['csrf_token'] = generate_csrf_token

# Initialize upload directories
try:
    init_upload_dirs()
    print("Upload directories initialized successfully")
except Exception as e:
    print(f"Error initializing upload directories: {e}")

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id: str) -> Optional[User]:
    """Load user from JSON store by user ID."""
    users = read_json('users.json', [])
    user_obj = next((u for u in users if u.get('id') == user_id), None)
    if not user_obj:
        return None
    return User(
        user_obj['id'],
        user_obj['email'],
        user_obj.get('password_hash', ''),
        is_admin=user_obj.get('is_admin', False)  # Make sure to load the admin flag
    )

# Import and register blueprints
# Register blueprints
app.register_blueprint(public_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(orders_bp)


@app.context_processor
def inject_now():
    """Inject current datetime into all templates."""
    return {'now': datetime.now()}


@app.template_filter('datetime')
def format_datetime(value: str | datetime, format: str = '%B %d, %Y') -> str:
    """Format a date time to (Default): Month DD, YYYY"""
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except ValueError:
            return value
    return value.strftime(format) if value else ''


@app.route('/health')
def health():
    return 'ok', 200


if __name__ == '__main__':
    # Start a simple background scheduler to publish scheduled content
    def scheduler_loop(interval: int = 60) -> None:
        while True:
            try:
                # Publish blog posts with publish_at
                posts = read_json('blog.json', [])
                changed = False
                for p in posts:
                    pub = p.get('publish_at')
                    if pub and not p.get('published'):
                        try:
                            when = datetime.fromisoformat(pub)
                            if when <= datetime.now():
                                p['published'] = True
                                changed = True
                        except Exception:
                            continue
                if changed:
                    write_json('blog.json', posts)

                # Publish products with publish_at
                products = read_json('products.json', [])
                changed_p = False
                for pr in products:
                    pub = pr.get('publish_at')
                    if pub and not pr.get('visible', False):
                        try:
                            when = datetime.fromisoformat(pub)
                            if when <= datetime.now():
                                pr['visible'] = True
                                changed_p = True
                        except Exception:
                            continue
                if changed_p:
                    write_json('products.json', products)
            except Exception:
                pass
            time.sleep(interval)

    t = threading.Thread(target=scheduler_loop, daemon=True)
    t.start()
    app.run(debug=True)
