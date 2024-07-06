import pytest
from app import app, db
from models import User, JournalEntry
from werkzeug.security import generate_password_hash
from test_config import TestConfig

@pytest.fixture
def client():
    app.config.from_object(TestConfig)
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

def test_register(client):
    response = client.post('/api/register', json={
        'username': 'testuser',
        'password': 'testpassword'
    })
    print('response', response)
    assert response.status_code == 201

def test_login(client):
    hashed_password = generate_password_hash('testpassword')
    user = User(username='testuser', password=hashed_password)
    db.session.add(user)
    db.session.commit()

    response = client.post('/api/login', json={
        'username': 'testuser',
        'password_hash': 'testpassword'
    })
    assert response.status_code == 200
    assert 'access_token' in response.get_json()

def test_add_entry(client):
    # Login first to get the access token
    hashed_password = generate_password_hash('testpassword')
    user = User(username='testuser', password=hashed_password)
    db.session.add(user)
    db.session.commit()

    login_response = client.post('/api/login', json={
        'username': 'testuser',
        'password': 'testpassword'
    })
    access_token = login_response.get_json()['access_token']

    # Add entry with access token
    print('client', client)
    response = client.post('/api/entries', json={
        'title': 'Test Entry',
        'content': 'This is a test entry.',
        'category': 'Test Category',
        'date': '2023-01-01'
    }, headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 201

def test_get_entries(client):
    # Login first to get the access token
    hashed_password = generate_password_hash('testpassword')
    user = User(username='testuser', password=hashed_password)
    db.session.add(user)
    db.session.commit()

    login_response = client.post('/api/login', json={
        'username': 'testuser',
        'password': 'testpassword'
    })
    access_token = login_response.get_json()['access_token']

    # Add an entry
    client.post('/api/entries', json={
        'title': 'Test Entry',
        'content': 'This is a test entry.',
        'category': 'Test Category',
        'date': '2023-01-01'
    }, headers={'Authorization': f'Bearer {access_token}'})

    # Get entries
    response = client.get('/api/entries', headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]['title'] == 'Test Entry'
