"""Run this script to reset the admin user
Usage: python scripts/reset_admin.py
"""
import sys
from pathlib import Path
import json
from werkzeug.security import generate_password_hash

# Make imports work
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

def reset_admin():
    """Reset to a single admin user with known credentials"""
    users_file = ROOT / 'data' / 'users.json'
    
    # Create new admin user
    users = [{
        'id': 'admin-1',
        'email': 'thabanghutamo@gmail.com',
        'password_hash': generate_password_hash('Password1'),
        'is_admin': True
    }]
    
    # Save to file
    with open(users_file, 'w') as f:
        json.dump(users, f, indent=2)
    
    print(f"Reset admin user: {users[0]['email']}")

if __name__ == '__main__':
    reset_admin()