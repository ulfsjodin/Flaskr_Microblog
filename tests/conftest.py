import os
import tempfile

import pytest
from flaskr import create_app
from flaskr.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf-8')

@pytest.fixture
def app():
    """Create and configure a new app instance for each test"""
    # create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()
    # create the app with common test config
    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
    })

    # create the database and load test data
    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    # close and remove the temporary database
    os.close(db_fd)
    os.unlink(db_path)
    
@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username = 'test', password = 'test'):
        return self._client.post(
            '/auth/login',
            data={'username' : username, 'password' : password}
        )

    def logout(self):
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    return AuthActions(client)
