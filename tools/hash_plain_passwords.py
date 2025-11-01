#!/usr/bin/env python3
"""
Safe helper to detect and optionally hash plaintext passwords in the `user` table.

Usage:
  # Dry-run: show which rows look like plaintext
  python tools/hash_plain_passwords.py --dry-run

  # Apply: actually replace plaintext values with werkzeug hashed passwords
  python tools/hash_plain_passwords.py --apply

Environment variables (optional):
  MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB

Notes:
- This script uses a simple heuristic to determine if a stored value "looks like" a hash:
  it checks for common hash prefixes (e.g., 'pbkdf2:', 'argon2', '$2b$') and minimum length.
- Always backup your DB before running with --apply.
"""

import os
import sys
import argparse
from werkzeug.security import generate_password_hash

try:
    import pymysql
except ImportError:
    print("Missing dependency 'pymysql'. Install with: pip install pymysql", file=sys.stderr)
    sys.exit(2)

HASH_PREFIXES = ('pbkdf2:', 'argon2', '$2b$', '$2y$', '$argon2')
MIN_HASH_LEN = 30


def looks_like_hash(s: str) -> bool:
    if not s:
        return False
    s = s.strip()
    if len(s) < MIN_HASH_LEN:
        return False
    for p in HASH_PREFIXES:
        if s.startswith(p):
            return True
    # fallback: if it contains a lot of $ signs (bcrypt-like)
    if s.count('$') >= 2:
        return True
    return False


def get_conn():
    return pymysql.connect(
        host=os.environ.get('MYSQL_HOST', 'localhost'),
        user=os.environ.get('MYSQL_USER', 'adminuser'),
        password=os.environ.get('MYSQL_PASSWORD', 'adminpassword'),
        db=os.environ.get('MYSQL_DB', 'transport'),
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
    )


def detect_and_hash(apply: bool):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT user_id, name, email, password_hash FROM `user`')
            rows = cur.fetchall()

            to_update = []
            for r in rows:
                val = r.get('password_hash') or ''
                if looks_like_hash(val):
                    # Already looks like a hash; skip
                    continue
                # otherwise treat as plaintext
                to_update.append(r)

            print(f"Found {len(to_update)} user(s) with probable plaintext passwords.")
            if not to_update:
                return 0

            for r in to_update:
                print(f" - user_id={r['user_id']} name={r['name']} email={r['email']} current='{r['password_hash']}'")

            if not apply:
                print('\nDry-run mode: no changes made. To apply changes run with --apply after backing up your DB.')
                return len(to_update)

            # Apply changes
            for r in to_update:
                new_hash = generate_password_hash((r.get('password_hash') or '').strip())
                cur.execute('UPDATE `user` SET password_hash=%s WHERE user_id=%s', (new_hash, r['user_id']))

            conn.commit()
            print(f"Updated {len(to_update)} user(s) to hashed passwords.")
            return len(to_update)
    finally:
        conn.close()


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument('--apply', action='store_true', help='Actually update detected plaintext passwords')
    p.add_argument('--dry-run', dest='dry', action='store_true', help='Only detect, do not change (default)')
    args = p.parse_args(argv)

    if args.dry:
        apply = False
    else:
        apply = args.apply

    if apply:
        print('Applying changes: updating plaintext passwords to secure hashes.')
        print('Make sure you have a DB backup before continuing.')
    else:
        print('Dry-run: detecting plaintext passwords (no changes).')

    try:
        n = detect_and_hash(apply)
        return 0 if n >= 0 else 1
    except Exception as e:
        print('Error:', e, file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
