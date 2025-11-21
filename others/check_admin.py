import sys
sys.path.insert(0, 'backend')
from database import execute_query

print('\nAll users in database:')
users = execute_query('SELECT username, email, user_type FROM users', fetch=True)
if users:
    for u in users:
        print(f'  Username: {u["username"]}, Email: {u["email"]}, Type: {u["user_type"]}')
else:
    print('  No users found')

