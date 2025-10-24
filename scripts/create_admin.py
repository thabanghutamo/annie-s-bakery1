"""Run this script to create an admin user in data/users.json
Usage: python scripts/create_admin.py

This module is import-safe and when executed will prompt for admin details.
"""
import sys
import os
import getpass
from werkzeug.security import generate_password_hash
from pathlib import Path
import argparse

# Make imports work even if the current working directory is different.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.json_store import read_json, write_json


def create_admin(email: str, password: str) -> bool:
    """Create an admin user and write to data/users.json. Returns True on success."""
    users = read_json('users.json', []) or []
    uid = 'admin-' + str(len(users) + 1)
    users.append({
        'id': uid,
        'email': email,
        'password_hash': generate_password_hash(password),
        'is_admin': True  # Make sure to set the admin flag
    })
    write_json('users.json', users)
    return True


def main():
    parser = argparse.ArgumentParser(description='Create an admin user for the app')
    parser.add_argument('--email', '-e', help='Admin email address')
    parser.add_argument('--password', '-p', help='Admin password (be careful: visible on process list)')
    args = parser.parse_args()

    # Interactive fallback if no CLI args provided
    if not args.email or not args.password:
        email = input('Admin email: ').strip()
        password = getpass.getpass('Password: ')
        password2 = getpass.getpass('Confirm password: ')
        if password != password2:
            print('Passwords do not match')
            return 1
        create_admin(email, password)
        print('Admin created:', email)
        return 0

    # Non-interactive mode
    create_admin(args.email, args.password)
    print('Admin created:', args.email)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
