import unittest
from unittest.mock import patch
import api.logic as logic

class TestLogic(unittest.TestCase):
    @patch('api.logic.fetch_cameras', return_value=[{"test": True}])
    def test_get_all_cameras(self, mock_fetch):
        result = logic.get_all_cameras()
        self.assertEqual(result, [{"test": True}])
        self.assertEqual(logic.get_cached_cameras(), [{"test": True}])

    @patch('api.logic.fetch_situations', return_value=[
        {
            "Deviation": [
                {
                    "LocationDescriptor": "Location 1",
                    "Message": "Message 1",
                    "StartTime": "2023-01-01T00:00:00",
                    "EndTime": "2023-01-02T00:00:00",
                    "SeverityText": "High",
                    "RoadNumber": "E4",
                    "Geometry": {
                        "Point": [{"WGS84": "POINT (18.0649 59.3326)"}]
                    }
                }
            ]
        }
    ])
    def test_get_all_accidents(self, mock_fetch):
        result = logic.get_all_accidents()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["location"], "Location 1")
        self.assertEqual(logic.get_cached_accidents(), result)

    @patch('api.logic.fetch_situations', return_value=[
        {
            "Deviation": [
                {
                    "LocationDescriptor": "Location 2",
                    "Message": "Message 2",
                    "StartTime": "2023-01-03T00:00:00",
                    "EndTime": "2023-01-04T00:00:00",
                    "SeverityText": "Low",
                    "RoadNumber": "E20",
                    "Geometry": {
                        "Point": [{"WGS84": "POINT (17.0639 58.1234)"}]
                    }
                }
            ]
        }
    ])
    def test_get_all_roadworks(self, mock_fetch):
        result = logic.get_all_roadworks()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["road"], "E20")
        self.assertEqual(logic.get_cached_roadworks(), result)

if __name__ == '__main__':
    unittest.main()
