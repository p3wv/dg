import re
import unittest
from app import create_app, db
from app.models import User, Role

class FlaskClientTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing') # type: ignore
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Stranger' in response.get_data(as_text=True))

    def test_register_and_login(self):
        # REGISTER
        response = self.client.post('/auth/register', data={
            'email': 'xhappyyxx@gmail.com',
            'username': 'john',
            'password': 'cat',
            'password2': 'cat'
        })
        self.assertEqual(response.status_code, 302)

        # LOGIN
        response = self.client.post('/auth/login', data={
            'email': 'xhappyyxx@gmail.com',
            'password': 'cat'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(re.search(r'Hello,[\s+]john!',
                                  response.get_data(as_text=True)))
        self.assertTrue(
            b'You have not confirmed your account yet' in response.get_data(
                as_text=True
            )
        )

        # send a confirmation token
        user = User.query.filter_by(email='xhappyyxx@gmail.com').first()
        token = user.generate_confirmation_token()
        response = self.client.get('/auth/confirm/{}'.format(token),
                                   follow_redirects=True)
        user.confirm(token)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            b'You have confirmed your account' in response.get_data(
                as_text=True))
        
        # LOGOUT
        response = self.client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'You have been logged out' in response.get_data(
            as_text=True))