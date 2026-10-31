import pytest
from app import app as flask_app
from database.db import init_db, get_db

@pytest.fixture
def app():
    flask_app.config.update({
        'TESTING': True,
        'DATABASE': ':memory:',  # Isolated in-memory DB per test
        'SECRET_KEY': 'test-secret',
        'WTF_CSRF_ENABLED': False,
    })

    # Since database/db.py uses a hardcoded DB_PATH, we need to monkeypatch it
    # for the :memory: DB to actually work if it's used inside get_db().
    # However, looking at database/db.py, it uses DB_PATH = "spendly.db".
    # For the sake of the test fixture, we will override the DB_PATH
    # by patching the module.
    import database.db
    database.db.DB_PATH = ':memory:'

    with flask_app.app_context():
        init_db()
        yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client):
    """A test client that is already logged in."""
    client.post('/register', data={'name': 'testuser', 'email': 'test@example.com', 'password': 'testpass'})
    client.post('/login', data={'email': 'test@example.com', 'password': 'testpass'})
    return client

def seed_test_expenses(user_id):
    """Helper to seed expenses for a specific user."""
    with get_db() as conn:
        expenses = [
            (user_id, 100.0, "Food", "2023-01-01", "Jan Food"),
            (user_id, 200.0, "Transport", "2023-01-15", "Jan Transport"),
            (user_id, 150.0, "Food", "2023-02-01", "Feb Food"),
            (user_id, 300.0, "Bills", "2023-03-01", "Mar Bills"),
            (user_id, 50.0, "Health", "2023-04-01", "Apr Health"),
        ]
        conn.executemany(
            "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
            expenses
        )
        conn.commit()

class TestProfileDateFilter:

    def test_profile_unauthenticated_redirects_to_login(self, client):
        """Unauthenticated access to /profile should redirect to login."""
        response = client.get('/profile')
        assert response.status_code == 302
        assert '/login' in response.location

    def test_profile_no_params_shows_all_data(self, auth_client):
        """/profile with no params should show unfiltered data (All Time)."""
        # Setup: get current user id
        with auth_client.session_transaction() as sess:
            user_id = sess['user_id']

        seed_test_expenses(user_id)

        response = auth_client.get('/profile')
        assert response.status_code == 200
        # Total = 100 + 200 + 150 + 300 + 50 = 800
        assert b'$800.00' in response.data
        assert b'5' in response.data  # Transaction count

    def test_profile_valid_date_range_filters_correctly(self, auth_client):
        """/profile with valid date_from and date_to should filter data."""
        with auth_client.session_transaction() as sess:
            user_id = sess['user_id']

        seed_test_expenses(user_id)

        # Filter for January 2023
        response = auth_client.get('/profile?date_from=2023-01-01&date_to=2023-01-31')
        assert response.status_code == 200
        # Total = 100 + 200 = 300
        assert b'$300.00' in response.data
        assert b'2' in response.data
        assert b'Jan Food' in response.data
        assert b'Jan Transport' in response.data
        assert b'Feb Food' not in response.data

    def test_profile_only_date_from_filters_correctly(self, auth_client):
        """/profile with only date_from should show expenses from that date onwards."""
        with auth_client.session_transaction() as sess:
            user_id = sess['user_id']

        seed_test_expenses(user_id)

        # From Feb 1st 2023 onwards
        response = auth_client.get('/profile?date_from=2023-02-01')
        assert response.status_code == 200
        # Total = 150 (Feb) + 300 (Mar) + 50 (Apr) = 500
        assert b'$500.00' in response.data
        assert b'3' in response.data

    def test_profile_only_date_to_filters_correctly(self, auth_client):
        """/profile with only date_to should show expenses up to that date."""
        with auth_client.session_transaction() as sess:
            user_id = sess['user_id']

        seed_test_expenses(user_id)

        # Up to Jan 31st 2023
        response = auth_client.get('/profile?date_to=2023-01-31')
        assert response.status_code == 200
        # Total = 100 + 200 = 300
        assert b'$300.00' in response.data
        assert b'2' in response.data

    def test_profile_invalid_date_order_flashes_error_and_falls_back(self, auth_client):
        """date_from > date_to should flash error and show all data."""
        with auth_client.session_transaction() as sess:
            user_id = sess['user_id']

        seed_test_expenses(user_id)

        # Invalid range: From 2023-02-01 to 2023-01-01
        response = auth_client.get('/profile?date_from=2023-02-01&date_to=2023-01-01')
        assert response.status_code == 200
        assert b'Start date must be before end date.' in response.data
        # Should fall back to All Time: $800.00
        assert b'$800.00' in response.data

    def test_profile_malformed_date_falls_back_silently(self, auth_client):
        """Malformed date strings should be ignored and fall back to unfiltered view."""
        with auth_client.session_transaction() as sess:
            user_id = sess['user_id']

        seed_test_expenses(user_id)

        # Malformed date_from
        response = auth_client.get('/profile?date_from=not-a-date')
        assert response.status_code == 200
        assert b'$800.00' in response.data

        # Malformed date_to
        response = auth_client.get('/profile?date_to=2023-13-45')
        assert response.status_code == 200
        assert b'$800.00' in response.data

    def test_profile_range_with_no_expenses_shows_zeroes(self, auth_client):
        """A range with no matching expenses should show zero/empty results."""
        with auth_client.session_transaction() as sess:
            user_id = sess['user_id']

        seed_test_expenses(user_id)

        # Range in 2024 (no expenses seeded)
        response = auth_client.get('/profile?date_from=2024-01-01&date_to=2024-01-31')
        assert response.status_code == 200
        assert b'$0.00' in response.data
        assert b'0' in response.data
        # Category breakdown should be empty (check for a common marker or lack of categories)
        # Since the spec says "empty category breakdown", we ensure the seeded ones aren't there
        assert b'Food' not in response.data
        assert b'Transport' not in response.data

    @pytest.mark.parametrize("date_from, date_to", [
        ("2023-01-01", "2023-01-31"), # Happy path
        ("not-a-date", "2023-01-31"), # One malformed
        ("2023-01-01", "not-a-date"), # Other malformed
        ("2023-05-01", "2023-01-01"), # Inverse order
    ])
    def test_profile_date_params_robustness(self, auth_client, date_from, date_to):
        """Test various date parameter combinations to ensure the app never crashes."""
        response = auth_client.get(f'/profile?date_from={date_from}&date_to={date_to}')
        assert response.status_code == 200
