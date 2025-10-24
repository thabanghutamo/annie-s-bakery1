"""Script to rehash all passwords in users.json to use a compatible hash method."""
import sys
from pathlib import Path

# Make imports work even if the current working directory is different.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.json_store import read_json, write_json
import getpass

def generate_safe_hash(password: str) -> str:
    """Generate a password hash that works across Werkzeug versions."""
    from werkzeug.security import generate_password_hash
    return generate_password_hash(password, method='pbkdf2:sha256')

def main():
    """Main function to rehash passwords."""
    # Load existing users
    users = read_json('users.json', [])
    if not users:
        print("No users found")
        return 1

    print(f"Found {len(users)} users")
    for user in users:
        print(f"\nUser: {user['email']}")
        password = getpass.getpass('Enter new password: ')
        password2 = getpass.getpass('Confirm password: ')
        if password != password2:
            print('Passwords do not match')
            return 1
        user['password_hash'] = generate_safe_hash(password)

    # Save updated users
    write_json('users.json', users)
    print("\nAll passwords have been rehashed")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())