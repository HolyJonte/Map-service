import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Lägg till admin/ i sys.path så vi kan importera admin_logic
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import admin_logic
from database.crud.newspaper_crud import *


class TestAdminLogic(unittest.TestCase):

    @patch("admin_logic.get_db_connection")
    @patch("admin_logic.generate_password_hash")
    def test_update_admin_password(self, mock_hash, mock_get_db):
        mock_hash.return_value = "hashedpass"
        mock_conn = MagicMock()
        mock_cursor = mock_conn.cursor.return_value
        mock_get_db.return_value = mock_conn

        admin_logic.update_admin_password("nytt_losen")

        mock_hash.assert_called_once_with("nytt_losen", method="scrypt")
        mock_cursor.execute.assert_called_once_with(
            "UPDATE users SET password = ? WHERE is_admin = 1",
            ("hashedpass",)
        )
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch("admin_logic.db_get_all_newspapers")
    def test_get_all_newspapers(self, mock_get):
        admin_logic.get_all_newspapers()
        mock_get.assert_called_once()

    @patch("admin_logic.db_add_newspaper")
    def test_add_newspaper(self, mock_add):
        admin_logic.add_newspaper("Tidningen", "mail@test.se", 120)
        mock_add.assert_called_once_with("Tidningen", "mail@test.se", 120)

    @patch("admin_logic.db_delete_newspaper")
    def test_delete_newspaper(self, mock_delete):
        admin_logic.delete_newspaper(5)
        mock_delete.assert_called_once_with(5)


if __name__ == "__main__":
    unittest.main()
