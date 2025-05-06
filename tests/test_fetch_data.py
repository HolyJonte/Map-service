import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Lägg till projektroten i PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api import fetch_data


class TestFetchData(unittest.TestCase):

    @patch('api.fetch_data.requests.post')
    def test_fetch_cameras_success(self, mock_post):
        # Simulera ett lyckat svar
        mock_response = MagicMock()
        mock_response.json.return_value = {'data': 'cameras'}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        result = fetch_data.fetch_cameras()
        self.assertEqual(result, {'data': 'cameras'})
        mock_post.assert_called_once()
        mock_response.raise_for_status.assert_called_once()

    @patch('api.fetch_data.requests.post')
    def test_fetch_situations_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {'data': 'situations'}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        result = fetch_data.fetch_situations()
        self.assertEqual(result, {'data': 'situations'})
        mock_post.assert_called_once()
        mock_response.raise_for_status.assert_called_once()

    @patch('api.fetch_data.requests.post')
    def test_fetch_cameras_failure(self, mock_post):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("API error")
        mock_post.return_value = mock_response

        with self.assertRaises(Exception):
            fetch_data.fetch_cameras()

    @patch('api.fetch_data.requests.post')
    def test_fetch_situations_failure(self, mock_post):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("API error")
        mock_post.return_value = mock_response

        with self.assertRaises(Exception):
            fetch_data.fetch_situations()


if __name__ == '__main__':
    unittest.main()
