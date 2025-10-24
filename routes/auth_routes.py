from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from utils.json_store import read_json, write_json
from models.user import User
import uuid

def generate_safe_hash(password: str) -> str:
    """Generate a password hash that works across Werkzeug versions."""
    return generate_password_hash(password, method='pbkdf2:sha256')

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Universal login route for both customers and admins"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        print(f"Login attempt for email: {email}")
        
        # Make sure we're looking in the right place for the users.json file
        try:
            # The json_store utility handles the data directory path
            users = read_json('users.json', [])
            print(f"Successfully loaded users.json, found {len(users)} users")
            
            # Try to find the user regardless of admin status
            matching_users = [u for u in users if u.get('email', '').lower() == email.lower()]
            user_obj = matching_users[0] if matching_users else None
            print(f"Email search: {email}, Found matches: {len(matching_users) if matching_users else 0}")
            
            if user_obj:
                print(f"Found user: {user_obj.get('email')}")
                print(f"User details - ID: {user_obj.get('id')}, Admin: {user_obj.get('is_admin')}")
                
                try:
                    if check_password_hash(user_obj.get('password_hash', ''), password):
                        # Create user object with correct admin status
                        is_admin = bool(user_obj.get('is_admin', False))
                        user = User(
                            user_obj['id'],
                            user_obj['email'],
                            user_obj['password_hash'],
                            is_admin=is_admin
                        )
                        print(f"User object created, is_admin: {user.is_admin}")
                        
                        if login_user(user):
                            print("Flask-Login login_user() successful")
                            if user.is_admin:
                                print("Admin user confirmed, redirecting to admin.dashboard")
                                return redirect(url_for('admin.dashboard'))
                            else:
                                print("Regular user confirmed, redirecting to public.dashboard")
                                next_page = request.args.get('next')
                                if next_page and next_page.startswith('/'):
                                    return redirect(next_page)
                                return redirect(url_for('public.dashboard'))
                        else:
                            print("Flask-Login login_user() failed")
                            flash('Login failed. Please try again.', 'danger')
                    else:
                        print("Password verification failed")
                        flash('Invalid password', 'danger')
                except Exception as e:
                    print(f"Error during password check: {str(e)}")
                    flash('An error occurred during login. Please try again.', 'danger')
            else:
                print(f"No user found with email: {email}")
                flash('No account found with this email address', 'danger')
                
        except Exception as e:
            print(f"Error loading users.json: {str(e)}")
            flash('System error. Please try again later.', 'danger')
            
    return render_template('auth/login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not all([email, password, confirm_password]):
            flash('All fields are required', 'danger')
            return render_template('public/register.html')

        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('public/register.html')

        users = read_json('users.json', [])
        if any(u.get('email') == email for u in users):
            flash('Email already registered', 'danger')
            return render_template('public/register.html')

        new_user = {
            'id': str(uuid.uuid4()),
            'email': email,
            'password_hash': generate_safe_hash(password),
            'is_admin': False
        }
        users.append(new_user)
        write_json('users.json', users)

        user = User(new_user['id'], new_user['email'], new_user['password_hash'])
        login_user(user)
        return redirect(url_for('public.dashboard'))

    return render_template('public/register.html')


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('public.home'))
