from app import app

# Use Flask test client to simulate a non-admin logged-in user
with app.test_client() as client:
    # Set up a session with role 'passenger'
    with client.session_transaction() as sess:
        sess['logged_in'] = True
        sess['user_id'] = 1
        sess['role'] = 'passenger'
        sess['username'] = 'testuser'

    resp = client.get('/routes', follow_redirects=False)
    print('Status code:', resp.status_code)
    # If redirect, Location header should point to /dashboard
    if resp.status_code in (301, 302):
        print('Location:', resp.headers.get('Location'))
    else:
        print('Response data (first 300 chars):')
        print(resp.get_data(as_text=True)[:300])
