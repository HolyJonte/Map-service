import unittest
from unittest.mock import patch
from flask import Flask
from api.routes import trafik_bp
import sys
import os

# Lägg till projektroten i PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestRoutes(unittest.TestCase):
    def setUp(self):
        app = Flask(__name__)
        app.register_blueprint(trafik_bp)
        self.client = app.test_client()

    def test_cameras_route(self):
        response = self.client.get('/cameras')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)

    def test_accidents_route(self):
        response = self.client.get('/accidents')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)

    def test_roadworks_route(self):
        response = self.client.get('/roadworks')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)

    def test_get_cameras_error(self):
        with patch('api.routes.get_cached_cameras', side_effect=Exception("Test error")):
            response = self.client.get('/cameras')
            self.assertEqual(response.status_code, 500)
            self.assertIn(b"Test error", response.data)

    def test_get_roadworks_error(self):
        with patch('api.routes.get_cached_roadworks', side_effect=Exception("Roadwork error")):
            response = self.client.get('/roadworks')
            self.assertEqual(response.status_code, 500)
            self.assertIn(b"Roadwork error", response.data)

    def test_get_accidents_error(self):
        with patch('api.routes.get_cached_accidents', side_effect=Exception("Accident error")):
            response = self.client.get('/accidents')
            self.assertEqual(response.status_code, 500)
            self.assertIn(b"Accident error", response.data)

if __name__ == '__main__':
    unittest.main()
