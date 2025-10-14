import pytest
from werkzeug.security import check_password_hash
from databaseTable import Account  # Make sure this path is correct


# ---------------- Fixtures ----------------
@pytest.fixture
def sample_user():
    """Fixture to create a sample Accounts instance."""
    return Account(
        username="testuser",
        email="test@example.com",
        password="securepassword123"
    )


# ---------------- Tests ----------------

def test_account_creation_fixture(sample_user):
    """Test that an Accounts object is created via fixture."""
    assert sample_user.username == "testuser"
    assert sample_user.email == "test@example.com"
    # Password should be hashed
    assert sample_user.password != "securepassword123"
    assert sample_user.password.startswith("pbkdf2:sha256:")


def test_account_creation_direct():
    """Test creating an Accounts object directly."""
    user = Account(
        username="directuser",
        email="direct@example.com",
        password="mypassword"
    )
    assert user.username == "directuser"
    assert user.email == "direct@example.com"
    assert user.password != "mypassword"
    assert user.password.startswith("pbkdf2:sha256:")


def test_password_is_hashed():
    """Ensure that the password is hashed correctly."""
    user = Account(
        username="hashuser",
        email="hash@example.com",
        password="hashpass"
    )
    assert check_password_hash(user.password, "hashpass") is True


def test_check_password_correct():
    """Test that checkPassword returns True for correct password."""
    user = Account(
        username="passuser",
        email="pass@example.com",
        password="rightpass"
    )
    assert user.checkPassword("rightpass") is True


def test_check_password_incorrect():
    """Test that checkPassword returns False for incorrect password."""
    user = Account(
        username="wrongpassuser",
        email="wrong@example.com",
        password="rightpass"
    )
    assert user.checkPassword("wrongpass") is False
