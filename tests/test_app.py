"""Tests use unittest + Flask test client so they run with `python -m unittest` or pytest."""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import create_app  # noqa: E402
from app.data import COMPARISON, admin_summary, synthetic_applications  # noqa: E402


class AppTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.app = create_app({"TESTING": True, "DB_PATH": os.path.join(self.tmp.name, "t.db"),
                               "STATUS_STEP_SECONDS": 1})
        self.c = self.app.test_client()

    def tearDown(self):
        self.tmp.cleanup()

    def submit(self, **over):
        body = {"service": "grievance", "alias": "Demo Citizen", "details": "Streetlight test"}
        body.update(over)
        return self.c.post("/api/applications", json=body)

    def test_home_and_disclaimer(self):
        r = self.c.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"academic simulation", r.data.lower())

    def test_health(self):
        self.assertEqual(self.c.get("/healthz").get_json(), {"status": "ok"})

    def test_security_headers(self):
        h = self.c.get("/").headers
        self.assertIn("default-src 'self'", h["Content-Security-Policy"])
        self.assertEqual(h["X-Content-Type-Options"], "nosniff")

    def test_comparison_covers_required_dimensions(self):
        dims = {d["dimension"] for d in COMPARISON}
        for needed in ("Flexibility to change", "Delivery frequency", "Testing", "Documentation",
                       "Stakeholder involvement", "Risks", "Advantages", "Limitations"):
            self.assertIn(needed, dims)
        data = self.c.get("/api/models").get_json()
        self.assertEqual(len(data["models"]), 3)

    def test_submit_and_track(self):
        r = self.submit()
        self.assertEqual(r.status_code, 201)
        ref = r.get_json()["ref"]
        t = self.c.get(f"/api/applications/{ref}")
        self.assertEqual(t.status_code, 200)
        self.assertEqual(t.get_json()["status"], "Submitted")

    def test_status_progresses(self):
        ref = self.submit().get_json()["ref"]
        import time
        time.sleep(3.2)
        self.assertEqual(self.c.get(f"/api/applications/{ref}").get_json()["status"], "Approved")

    def test_rejects_bad_service_and_alias(self):
        self.assertEqual(self.submit(service="nope").status_code, 400)
        self.assertEqual(self.submit(alias="x").status_code, 400)

    def test_rejects_personal_data_patterns(self):
        self.assertEqual(self.submit(details="mail me at a@b.com").status_code, 400)
        self.assertEqual(self.submit(details="id 1234 5678 9012").status_code, 400)

    def test_bad_and_unknown_reference(self):
        self.assertEqual(self.c.get("/api/applications/abc").status_code, 400)
        self.assertEqual(self.c.get("/api/applications/SIM-00000000").status_code, 404)

    def test_sql_injection_string_is_harmless(self):
        self.assertEqual(self.c.get("/api/applications/SIM-1'%20OR%201=1--").status_code, 400)
        self.assertEqual(self.submit(alias="x'); DROP TABLE applications;--").status_code, 201)
        self.assertEqual(self.submit().status_code, 201)

    def test_admin_summary_is_synthetic_and_deterministic(self):
        s = admin_summary()
        self.assertTrue(s["synthetic"])
        self.assertEqual(s["total"], 60)
        self.assertEqual(synthetic_applications(), synthetic_applications())
        self.assertEqual(sum(s["by_status"].values()), 60)
        self.assertEqual(self.c.get("/api/admin/summary").status_code, 200)


if __name__ == "__main__":
    unittest.main()
