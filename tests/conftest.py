import os
import tempfile

import pytest

from flaskr import create_app
from flaskr.db import init_db, get_db

with open(os.path.join(os.path.dirname(__file__), "data.sql"), "rb") as f:
    _data_sql = f.read().decode("utf8")


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    '''
    tempfile.mkstemp() 
        creates and opens a temporary file, 
        returning the file descriptor and the path to it. 
    '''

    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
    })

    '''
    TESTING tells Flask that the app is in tests mode. 
    Flask changes some internal behavior so it’s easier to tests, 
    and other extensions can also use the flag to make testing them easier.
    
    The DATABASE path is overridden 
    so it points to this temporary path instead of the instance folder.    
    '''

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    os.close(db_fd)
    os.unlink(db_path)

    '''
    After setting the path, the database tables are created and the tests data is inserted. 
    After the tests is over, the temporary file is closed and removed.
    '''


@pytest.fixture
def client(app):
    return app.test_client()

    '''
    The client fixture calls app.test_client() 
    with the application object created by the app fixture. 
    Tests will use the client to make requests to the application 
    without running the server.
    '''


@pytest.fixture
def runner(app):
    return app.test_cli_runner()

    '''
    The runner fixture is similar to client. app.test_cli_runner() creates a runner 
    that can call the Click commands registered with the application.
    '''


class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    return AuthActions(client)
