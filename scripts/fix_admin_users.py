"""Run this script to fix admin users by adding the is_admin flag
Usage: python scripts/fix_admin_users.py
"""
import sys
from pathlib import Path
from typing import List, Dict, Any

# Make imports work even if the current working directory is different.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.json_store import read_json, write_json


def fix_admin_users() -> None:
    """Add is_admin flag to existing admin users."""
    users: List[Dict[str, Any]] = read_json('users.json', [])
    modified = False
    
    for user in users:
        # Check if user is an admin based on their ID
        is_admin_id = user['id'].startswith('admin-') or user['id'] == 'admin'
        if is_admin_id and not user.get('is_admin'):
            user['is_admin'] = True
            modified = True
    
    if modified:
        write_json('users.json', users)
        print('Updated admin flags in users.json')
    else:
        print('No changes needed')


if __name__ == '__main__':
    fix_admin_users()