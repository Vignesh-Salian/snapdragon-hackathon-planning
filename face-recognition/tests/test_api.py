"""
test_api.py
HemaGrid AI - Donor Verification API Unit Tests

Tests FastAPI route logic, database serialization, and duplicate verification
logic by mocking face landmark detection operations.
"""

import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from api.main import app, db

class TestDonorVerificationAPI(unittest.TestCase):
    def setUp(self):
        # Bind TestClient
        self.client = TestClient(app)
        # Initialize/clean test database
        db.clear_database()

    def tearDown(self):
        # Cleanup records
        db.clear_database()

    def test_health_check(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "healthy")

    @patch("api.main.detector.extract_landmarks")
    def test_enroll_success(self, mock_extract):
        # Configure mock to return dummy face landmarks (1404 values)
        dummy_landmarks = [0.1] * 1404
        mock_extract.return_value = dummy_landmarks

        # Run mock image upload request
        files = {"image": ("test.jpg", b"fake_image_bytes", "image/jpeg")}
        data = {"name": "Alice Smith"}
        
        response = self.client.post("/api/v1/donor/enroll", data=data, files=files)
        self.assertEqual(response.status_code, 200)
        
        json_data = response.json()
        self.assertEqual(json_data["status"], "success")
        self.assertIn("donor_id", json_data)

    @patch("api.main.detector.extract_landmarks")
    def test_enroll_no_face(self, mock_extract):
        # Configure mock to simulate no face detected
        mock_extract.return_value = None

        files = {"image": ("test.jpg", b"fake_image_bytes", "image/jpeg")}
        data = {"name": "Bob Jones"}
        
        response = self.client.post("/api/v1/donor/enroll", data=data, files=files)
        self.assertEqual(response.status_code, 400)
        self.assertIn("No face detected", response.json()["detail"])

    @patch("api.main.detector.extract_landmarks")
    def test_verify_no_duplicate(self, mock_extract):
        # Mock returns landmark array
        mock_extract.return_value = [0.5] * 1404
        
        files = {"image": ("test.jpg", b"fake_image_bytes", "image/jpeg")}
        response = self.client.post("/api/v1/donor/verify", files=files)
        
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["duplicate_detected"])

    @patch("api.main.detector.extract_landmarks")
    def test_verify_duplicate_detected(self, mock_extract):
        # 1. Enroll a donor with specific landmark values
        landmarks_a = [0.1] * 1404
        db.enroll_donor("Charlie Brown", landmarks_a)

        # 2. Mock detector to return identical landmarks on input image
        mock_extract.return_value = landmarks_a

        files = {"image": ("test.jpg", b"fake_image_bytes", "image/jpeg")}
        response = self.client.post("/api/v1/donor/verify", files=files)
        
        self.assertEqual(response.status_code, 409)
        json_data = response.json()
        self.assertTrue(json_data["duplicate_detected"])
        self.assertEqual(json_data["matched_donor"]["name"], "Charlie Brown")

if __name__ == "__main__":
    unittest.main()
