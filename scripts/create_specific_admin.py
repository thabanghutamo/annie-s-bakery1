"""Run this script to create a specific admin user
Usage: python scripts/create_specific_admin.py
"""
import sys
from pathlib import Path
import json
from werkzeug.security import generate_password_hash

# Make imports work
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

def create_admin():
    """Create a specific admin user with known credentials"""
    # Read existing users
    users_file = ROOT / 'data' / 'users.json'
    try:
        with open(users_file, 'r') as f:
            users = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        users = []
    
    # Remove any existing users with this email
    users = [u for u in users if u.get('email') != 'thabanghutamo@gmail.com']
    
    # Create new admin user
    new_admin = {
        'id': 'admin-1',
        'email': 'thabanghutamo@gmail.com',
        'password_hash': generate_password_hash('Password1'),
        'is_admin': True
    }
    
    users.append(new_admin)
    
    # Save back to file
    with open(users_file, 'w') as f:
        json.dump(users, f, indent=2)
    
    print(f"Created admin user: {new_admin['email']}")

if __name__ == '__main__':
    create_admin()