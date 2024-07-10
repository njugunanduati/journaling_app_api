import pytest
from app import app, db
from models import User, JournalEntry
from utils import hash_password, verify_password
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
    assert response.status_code == 201

def test_password_hash(client):
    hashed_password = hash_password('testpassword')
    assert verify_password('testpassword', hashed_password)

def test_login(client):
    response = client.post('/api/login', json={
        'username': 'testuser',
        'password': 'testpassword'
    })
    assert response.status_code == 200
    assert 'access_token' in response.get_json()


def test_get_profile(client):
    # Login first to get the access token
    hashed_password = hash_password('testpassword')
    user = User(username='testuser', password=hashed_password)
    db.session.add(user)
    db.session.commit()

    login_response = client.post('/api/login', json={
        'username': 'testuser',
        'password': 'testpassword'
    })
    access_token = login_response.get_json()['access_token']

    # Get profile with access token
    response = client.get('/api/profile', headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 200
    assert 'username' in response.get_json()
    assert 'username' == 'testuser'
    assert 'first_name' in response.get_json()
    assert 'last_name' in response.get_json()

def test_update_entry(client):
    # Login first to get the access token
    hashed_password = hash_password('testpassword')
    user = User(username='testuser', password=hashed_password)
    db.session.add(user)
    db.session.commit()

    login_response = client.post('/api/login', json={
        'username': 'testuser',
        'password': 'testpassword'
    })
    access_token = login_response.get_json()['access_token']

    # Add entry first
    client.post('/api/entries', json={
        'title': 'Test Entry',
        'content': 'This is a test entry.',
        'category': 'Test Category',
        'date': '2023-01-01'
    }, headers={'Authorization': f'Bearer {access_token}'})

    # Get entry ID
    entry_response = client.get('/api/entries', headers={'Authorization': f'Bearer {access_token}'})
    entry_id = entry_response.get_json()[0]['id']

    # Update entry 
    response = client.put(f'/api/entries/{entry_id}', json={
        'title': 'Updated Test Entry',
        'content': 'This is an updated test entry.',
        'category': 'Updated Test Category',
        'date': '2023-02-01'
    }, headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 200

    # Get updated entry
    updated_entry_response = client.get(f'/api/entries/{entry_id}', headers={'Authorization': f'Bearer {access_token}'})
    assert updated_entry_response.get_json()['title'] == 'Updated Test Entry'
    assert updated_entry_response.get_json()['content'] == 'This is an updated test entry.'
    assert updated_entry_response.get_json()['category'] == 'Updated Test Category'

    # Delete entry
    delete_response = client.delete(f'/api/entries/{entry_id}', headers={'Authorization': f'Bearer {access_token}'})
    assert delete_response.status_code == 200
def test_add_entry(client):
    # Login first to get the access token
    hashed_password = hash_password('testpassword')
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
    hashed_password = hash_password('testpassword')
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
