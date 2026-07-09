"""
test_backend.py
HemaGrid AI - Core Backend Integration Tests

Unit tests validating inventory REST APIs, SQL database commits,
telemetry intake, and WebSocket dispatch operations.
"""

import unittest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from api.main import app, get_db, manager
from database.models import init_db, SessionLocal, Hospital, Inventory

class TestCoreBackend(unittest.TestCase):
    def setUp(self):
        # Create tables and load data
        init_db()
        self.client = TestClient(app)
        
        # Clean up database transactions before each test
        self.db = SessionLocal()
        # Verify initial baseline
        if self.db.query(Hospital).count() == 0:
            h = Hospital(id=1, name="Test General", hospital_type="General")
            self.db.add(h)
            self.db.commit()

    def tearDown(self):
        self.db.close()

    def test_health_check(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "healthy")

    def test_get_inventory_success(self):
        response = self.client.get("/api/v1/inventory/1")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("hospital_name", data)
        self.assertIn("inventory", data)

    def test_get_inventory_not_found(self):
        response = self.client.get("/api/v1/inventory/999")
        self.assertEqual(response.status_code, 404)

    def test_update_inventory_success(self):
        # First ensure the stock record exists
        stock = self.db.query(Inventory).filter(
            Inventory.hospital_id == 1,
            Inventory.blood_type == "O_NEG"
        ).first()
        
        initial_val = stock.units_available if stock else 0

        payload = {
            "hospital_id": 1,
            "blood_type": "O_NEG",
            "units_added_removed": 10
        }
        
        response = self.client.post("/api/v1/inventory/update", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["updated_total"], initial_val + 10)

    def test_update_inventory_negative_total_fails(self):
        # Set stock level to 5
        stock = self.db.query(Inventory).filter(
            Inventory.hospital_id == 1,
            Inventory.blood_type == "A_POS"
        ).first()
        
        if not stock:
            stock = Inventory(hospital_id=1, blood_type="A_POS", units_available=5)
            self.db.add(stock)
        else:
            stock.units_available = 5
        self.db.commit()

        # Try to remove 10 units (resulting in -5)
        payload = {
            "hospital_id": 1,
            "blood_type": "A_POS",
            "units_added_removed": -10
        }
        
        response = self.client.post("/api/v1/inventory/update", json=payload)
        self.assertEqual(response.status_code, 400)

    @patch("api.main.manager.broadcast", new_callable=AsyncMock)
    def test_telemetry_intake_broadcasts(self, mock_broadcast):
        payload = {
            "device_id": "box_99",
            "uptime_ms": 5000,
            "telemetry": {
                "temperature_c": 5.5,
                "humidity_pct": 60.0,
                "acceleration_g": 0.1,
                "max_impact_g": 1.2
            },
            "status": {
                "state": "SAFE",
                "flags": {
                    "temp_breached": False,
                    "impact_breached": False
                }
            }
        }
        
        response = self.client.post("/api/v1/telemetry/report", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("logged_id", response.json())
        
        # Verify WebSocket broadcast was triggered
        mock_broadcast.assert_called_once()
        broadcast_arg = mock_broadcast.call_args[0][0]
        self.assertEqual(broadcast_arg["event_type"], "TELEMETRY_UPDATE")
        self.assertEqual(broadcast_arg["data"]["device_id"], "box_99")
        self.assertEqual(broadcast_arg["data"]["state"], "SAFE")

if __name__ == "__main__":
    unittest.main()
