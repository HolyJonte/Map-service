import unittest
from unittest.mock import patch, MagicMock
import sys
import os
from flask import Flask

# Sätt projektrot som PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ..admin.admin_routes import admin_routes


class TestAdminRoutes(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.secret_key = 'test'
        self.app.register_blueprint(admin_routes)
        self.client = self.app.test_client()

    def test_redirect_if_not_logged_in(self):
        with self.app.test_request_context():
            with patch('admin.admin_routes.session', {'admin_logged_in': False}), \
                 patch('admin.admin_routes.url_for', return_value='/login'):
                response = self.client.get('/admin/dashboard')
                self.assertEqual(response.status_code, 302)
                self.assertIn('/login', response.location)

    def test_render_dashboard_logged_in(self):
        with self.app.test_request_context():
            with patch('admin.admin_routes.session', {'admin_logged_in': True}), \
                 patch('admin.admin_routes.get_all_newspapers', return_value=['Test']), \
                 patch('admin.admin_routes.render_template', return_value='dashboard'):
                response = self.client.get('/admin/dashboard')
                self.assertEqual(response.data, b'dashboard')

    def test_add_newspaper(self):
        with patch('admin.admin_routes.session', {'admin_logged_in': True}), \
             patch('admin.admin_routes.add_newspaper') as mock_add, \
             patch('admin.admin_routes.get_all_newspapers', return_value=[]), \
             patch('admin.admin_routes.render_template', return_value='OK'):
            response = self.client.post('/admin/dashboard', data={
                'action': 'add',
                'name': 'DN',
                'contact_email': 'dn@example.com',
                'sms_quota': '100'
            })
            mock_add.assert_called_once_with('DN', 'dn@example.com', 100)
            self.assertEqual(response.data, b'OK')

    def test_add_newspaper_missing_name(self):
        with patch('admin.admin_routes.session', {'admin_logged_in': True}), \
             patch('admin.admin_routes.add_newspaper') as mock_add, \
             patch('admin.admin_routes.get_all_newspapers', return_value=[]), \
             patch('admin.admin_routes.render_template', return_value='OK'):
            response = self.client.post('/admin/dashboard', data={
                'action': 'add',
                'contact_email': 'dn@example.com',
                'sms_quota': '100'
            })
            mock_add.assert_not_called()
            self.assertEqual(response.data, b'OK')

    def test_delete_newspaper(self):
        with patch('admin.admin_routes.session', {'admin_logged_in': True}), \
             patch('admin.admin_routes.delete_newspaper') as mock_delete, \
             patch('admin.admin_routes.get_all_newspapers', return_value=[]), \
             patch('admin.admin_routes.render_template', return_value='OK'):
            response = self.client.post('/admin/dashboard', data={
                'action': 'delete',
                'id': '5'
            })
            mock_delete.assert_called_once_with(5)
            self.assertEqual(response.data, b'OK')

    def test_delete_newspaper_missing_id(self):
        with patch('admin.admin_routes.session', {'admin_logged_in': True}), \
             patch('admin.admin_routes.delete_newspaper') as mock_delete, \
             patch('admin.admin_routes.get_all_newspapers', return_value=[]), \
             patch('admin.admin_routes.render_template', return_value='OK'):
            response = self.client.post('/admin/dashboard', data={
                'action': 'delete'
            })
            mock_delete.assert_not_called()
            self.assertEqual(response.data, b'OK')

    def test_change_password_success(self):
        with patch('admin.admin_routes.session', {'admin_logged_in': True}), \
             patch('admin.admin_routes.update_admin_password') as mock_update, \
             patch('admin.admin_routes.get_all_newspapers', return_value=[]), \
             patch('admin.admin_routes.render_template', return_value='OK'):
            response = self.client.post('/admin/dashboard', data={
                'action': 'change_password',
                'new_password': 'abc',
                'confirm_password': 'abc'
            })
            mock_update.assert_called_once_with('abc')
            self.assertEqual(response.data, b'OK')

    def test_change_password_mismatch(self):
        with patch('admin.admin_routes.session', {'admin_logged_in': True}), \
             patch('admin.admin_routes.get_all_newspapers', return_value=[]), \
             patch('admin.admin_routes.render_template', return_value='error'):
            response = self.client.post('/admin/dashboard', data={
                'action': 'change_password',
                'new_password': 'abc',
                'confirm_password': 'xyz'
            })
            self.assertEqual(response.data, b'error')

    def test_logout(self):
        with self.app.test_request_context():
            mock_session = MagicMock()
            with patch('admin.admin_routes.session', mock_session), \
                 patch('admin.admin_routes.url_for', return_value='/index'), \
                 patch('admin.admin_routes.redirect', return_value='redirected'):
                response = self.client.get('/admin/logout')
                mock_session.pop.assert_called_once_with('admin_logged_in', None)
                self.assertEqual(response.data, b'redirected')


if __name__ == '__main__':
    unittest.main()
