import pytest
from flask import Flask, session
from accRoute import bp


@pytest.fixture
def app():
    """Create a Flask test app and register blueprint."""
    app = Flask(__name__)
    app.secret_key = "test_secret"
    app.register_blueprint(bp)
    return app


@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()


# ---------------- HOME PAGE ----------------
def test_home_route(client):
    response = client.get("/")
    assert response.status_code == 200
    # The template name won't show, but basic HTML structure should be present
    assert b"<" in response.data


# ---------------- CREATE ACCOUNT ----------------
def test_create_account_new_user(monkeypatch, client):
    """Test creating a new account successfully."""

    class DummyQuery:
        def filter_by(self, **kwargs):
            return self

        def first(self):
            # No user exists
            return None

    class DummyAccounts:
        query = DummyQuery()

        def __init__(self, username, email, password):
            self.username = username
            self.email = email
            self.password = password

    class DummySession:
        def add(self, obj):
            self.added = obj

        def commit(self):
            self.committed = True

    dummy_session = DummySession()

    # Apply monkeypatches
    monkeypatch.setattr("accRoute.Accounts", DummyAccounts)
    monkeypatch.setattr("accRoute.maftleAcc", type("db", (), {"session": dummy_session}))

    response = client.post(
        "/createaccount.html",
        data={"username": "newuser", "email": "new@example.com", "password": "pass"},
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert "/loginpage.html" in response.headers["Location"]
    assert hasattr(dummy_session, "added")
    assert hasattr(dummy_session, "committed")


def test_create_account_existing_username(monkeypatch, client):
    """Test when username already exists."""

    class DummyQuery:
        def __init__(self):
            self.call = 0

        def filter_by(self, **kwargs):
            self.call += 1
            return self

        def first(self):
            # First query (username) returns a user
            return True if self.call == 1 else None

    class DummyAccounts:
        query = DummyQuery()

    monkeypatch.setattr("accRoute.Accounts", DummyAccounts)

    response = client.post(
        "/createaccount.html",
        data={"username": "existing", "email": "new@example.com", "password": "pass"},
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert "/createaccount.html" in response.headers["Location"]


def test_create_account_existing_email(monkeypatch, client):
    """Test when email already exists."""

    class DummyQuery:
        def __init__(self):
            self.call = 0

        def filter_by(self, **kwargs):
            self.call += 1
            return self

        def first(self):
            # First query returns None (username free), second returns True (email taken)
            return None if self.call == 1 else True

    class DummyAccounts:
        query = DummyQuery()

    monkeypatch.setattr("accRoute.Accounts", DummyAccounts)

    response = client.post(
        "/createaccount.html",
        data={"username": "newuser", "email": "exists@example.com", "password": "pass"},
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert "/createaccount.html" in response.headers["Location"]


# ---------------- LOGIN ----------------
def test_login_success(monkeypatch, client):
    """Test successful login with correct password."""

    class DummyUser:
        id = 1
        email = "user@example.com"
        username = "testuser"

        def checkPassword(self, password):
            return password == "correct"

    class DummyQuery:
        def filter_by(self, **kwargs):
            return self

        def first(self):
            return DummyUser()

    class DummyAccounts:
        query = DummyQuery()

    monkeypatch.setattr("accRoute.Accounts", DummyAccounts)

    response = client.post(
        "/loginpage.html",
        data={"email": "user@example.com", "password": "correct"},
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_login_failure(monkeypatch, client):
    """Test login with incorrect password."""

    class DummyUser:
        def checkPassword(self, password):
            return False

    class DummyQuery:
        def filter_by(self, **kwargs):
            return self

        def first(self):
            return DummyUser()

    class DummyAccounts:
        query = DummyQuery()

    monkeypatch.setattr("accRoute.Accounts", DummyAccounts)

    response = client.post(
        "/loginpage.html",
        data={"email": "wrong@example.com", "password": "badpass"},
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert "/loginpage.html" in response.headers["Location"]


def test_login_get_request(client):
    """GET should render login page."""
    response = client.get("/loginpage.html")
    assert response.status_code == 200


# ---------------- AUTH STATUS ----------------
def test_auth_status_logged_in(client):
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["username"] = "loggedinuser"

    response = client.get("/auth/status")
    data = response.get_json()
    assert data["logged_in"] is True
    assert data["username"] == "loggedinuser"


def test_auth_status_logged_out(client):
    response = client.get("/auth/status")
    data = response.get_json()
    assert data["logged_in"] is False


# ---------------- LOGOUT ----------------
def test_logout_clears_session(client):
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["username"] = "user"

    response = client.get("/logoutpage.html")
    assert response.status_code == 200
    # session should be cleared
    with client.session_transaction() as sess:
        assert "user_id" not in sess