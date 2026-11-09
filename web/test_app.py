"""Smoke tests: python -m unittest discover -s web"""
import os
import unittest

os.environ['DATABASE_URL'] = 'sqlite://'  # in-memory
os.environ['SECRET_KEY'] = 'test-only-secret'
os.environ['ADMIN_PASSWORD'] = 'test-admin-pw'
os.environ.setdefault('SESSION_COOKIE_SECURE', 'false')

from app import app, seed_sample_data, get_placement_statistics, get_key_statistics  # noqa: E402


class AppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
        with app.app_context():
            seed_sample_data(reset=True)

    def setUp(self):
        self.client = app.test_client()

    def login(self, password='test-admin-pw', next_url=None):
        url = '/login' + (f'?next={next_url}' if next_url else '')
        return self.client.post(url, data={'username': 'admin', 'password': password})

    def test_public_pages(self):
        self.assertEqual(self.client.get('/').status_code, 200)
        self.assertEqual(self.client.get('/login').status_code, 200)
        self.assertEqual(self.client.get('/nope').status_code, 404)

    def test_protected_pages_redirect(self):
        for path in ('/dashboard', '/students', '/companies', '/analysis'):
            self.assertEqual(self.client.get(path).status_code, 302, path)

    def test_login_and_pages(self):
        self.assertIn('Invalid', self.login('wrong').get_data(as_text=True))
        self.assertEqual(self.login().status_code, 302)
        for path in ('/dashboard', '/students', '/companies', '/analysis'):
            body = self.client.get(path).get_data(as_text=True)
            self.assertIn('Placement Tracker', body, path)
        self.assertIn('data-chart="chart-package_distribution"',
                      self.client.get('/analysis').get_data(as_text=True))

    def test_logout_requires_post(self):
        self.login()
        self.assertEqual(self.client.get('/logout').status_code, 405)
        self.client.post('/logout')
        self.assertEqual(self.client.get('/dashboard').status_code, 302)

    def test_login_rejects_open_redirect(self):
        response = self.login(next_url='https://evil.example/')
        self.assertTrue(response.headers['Location'].endswith('/dashboard'))
        self.client.post('/logout')
        response = self.login(next_url='/students')
        self.assertTrue(response.headers['Location'].endswith('/students'))

    def test_statistics(self):
        with app.app_context():
            stats = get_placement_statistics()
            summary = get_key_statistics()
        self.assertEqual(len(stats), 4)
        self.assertEqual(stats['total_offers'].sum(), 30)
        self.assertEqual(stats['accepted_offers'].sum(), 20)
        self.assertTrue((stats['placement_rate'] <= 100).all())
        self.assertEqual(summary['total_students'], 20)
        self.assertLessEqual(summary['placed_students'], 20)


class CsrfTests(unittest.TestCase):
    def test_login_without_csrf_token_is_rejected(self):
        app.config.update(WTF_CSRF_ENABLED=True)
        try:
            response = app.test_client().post('/login', data={'username': 'admin', 'password': 'x'})
            self.assertEqual(response.status_code, 400)
        finally:
            app.config.update(WTF_CSRF_ENABLED=False)


if __name__ == '__main__':
    unittest.main()
