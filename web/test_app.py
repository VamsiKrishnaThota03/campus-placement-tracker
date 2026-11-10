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


class SecurityHeaderTests(unittest.TestCase):
    """Flask sends none of these by default.

    They produce no visible symptom when they go missing, so a refactor can
    drop them silently — which is exactly why they are asserted here.
    """

    def setUp(self):
        app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
        self.client = app.test_client()

    def test_headers_present_on_every_response(self):
        for path in ('/', '/login'):
            with self.subTest(path=path):
                headers = self.client.get(path).headers
                self.assertEqual(headers['X-Content-Type-Options'], 'nosniff')
                self.assertEqual(headers['X-Frame-Options'], 'DENY')
                self.assertEqual(
                    headers['Referrer-Policy'], 'strict-origin-when-cross-origin'
                )
                self.assertIn('Content-Security-Policy', headers)
                self.assertIn('Permissions-Policy', headers)

    def test_csp_allows_the_cdns_the_templates_actually_load(self):
        csp = self.client.get('/').headers['Content-Security-Policy']
        # Templates pull Bootstrap and Bootstrap Icons from jsDelivr and Plotly
        # from its own CDN. A CSP that forgot these would silently break every
        # chart and all styling rather than failing server-side.
        self.assertIn('https://cdn.jsdelivr.net', csp)
        self.assertIn('https://cdn.plot.ly', csp)

    def test_csp_denies_framing_objects_and_base_uri_rewrites(self):
        csp = self.client.get('/').headers['Content-Security-Policy']
        for directive in (
            "frame-ancestors 'none'",
            "object-src 'none'",
            "base-uri 'none'",
            "form-action 'self'",
            "default-src 'self'",
        ):
            with self.subTest(directive=directive):
                self.assertIn(directive, csp)

    def test_hsts_is_not_sent_from_a_plain_http_dev_server(self):
        # SESSION_COOKIE_SECURE is false in this suite, standing in for a
        # plain-HTTP deployment. Announcing HSTS there would make the browser
        # refuse plain HTTP to the host for a year.
        self.assertNotIn(
            'Strict-Transport-Security', self.client.get('/').headers
        )


class CsrfProtectionTests(unittest.TestCase):
    """CSRFProtect is registered; confirm it is not inert."""

    def setUp(self):
        # CSRF is disabled for the other suites so they can post forms. Turn it
        # back on here, otherwise this asserts nothing.
        app.config.update(TESTING=True, WTF_CSRF_ENABLED=True)
        self.client = app.test_client()

    def tearDown(self):
        app.config.update(WTF_CSRF_ENABLED=False)

    def test_login_form_carries_a_csrf_token(self):
        body = self.client.get('/login').get_data(as_text=True)
        self.assertIn('csrf_token', body)

    def test_a_post_without_a_token_is_rejected(self):
        response = self.client.post(
            '/login', data={'username': 'admin', 'password': 'test-admin-pw'}
        )
        # 400 from CSRFProtect; the important part is that it is not a redirect
        # to the dashboard, which would mean the login succeeded unprotected.
        self.assertEqual(response.status_code, 400)
