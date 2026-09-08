import unittest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import Mock, patch
from uuid import uuid4

import httpx

from app.config import Settings
from app.models import Technology
from app.nvd import _request_cves, fetch_cves, persist_cves, technology_cpe


class NvdTests(unittest.TestCase):
    def test_maps_known_technology_to_cpe(self):
        technology = Technology(name="Nginx", version="1.24.0", category="server", source="nuclei")
        self.assertEqual(
            technology_cpe(technology),
            "cpe:2.3:a:f5:nginx:1.24.0:*:*:*:*:*:*:*",
        )

    def test_unknown_or_unversioned_technology_has_no_cpe(self):
        self.assertIsNone(technology_cpe(Technology(name="Custom CMS", version="1.0", category="CMS", source="nuclei")))
        self.assertIsNone(technology_cpe(Technology(name="Nginx", version=None, category="server", source="nuclei")))

    @patch("app.nvd.time.sleep")
    @patch("app.nvd.httpx.Client")
    def test_retries_transient_nvd_failure_without_logging_key(self, client_factory, sleep):
        first = Mock(status_code=503)
        first.raise_for_status.side_effect = httpx.HTTPStatusError("temporary", request=Mock(), response=first)
        second = Mock(status_code=200)
        second.json.return_value = {"vulnerabilities": [{"cve": {"id": "CVE-2024-0001"}}]}
        client = client_factory.return_value.__enter__.return_value
        client.get.side_effect = [first, second]
        settings = Settings(nvd_api_key="secret-key")
        result = _request_cves("cpe:2.3:a:f5:nginx:1.24.0:*:*:*:*:*:*:*", settings)
        self.assertEqual(result[0]["cve"]["id"], "CVE-2024-0001")
        self.assertEqual(client.get.call_args.kwargs["headers"], {"apiKey": "secret-key"})
        self.assertNotIn("secret-key", str(sleep.mock_calls))

    def test_uses_fresh_cache_without_network(self):
        technology = Technology(name="Nginx", version="1.24.0", category="server", source="nuclei")
        cache = SimpleNamespace(
            response_body=[{"cve": {"id": "CVE-2024-0001"}}],
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        db = Mock()
        db.get.return_value = cache
        with patch("app.nvd._request_cves") as request:
            result = fetch_cves(db, technology, Settings())
        self.assertEqual(result[0]["cve"]["id"], "CVE-2024-0001")
        request.assert_not_called()

    def test_persist_cves_is_idempotent_for_existing_ids(self):
        technology = Technology(name="Nginx", version="1.24.0", category="server", source="nuclei")
        technology.id = uuid4()
        existing = SimpleNamespace(cve_id="CVE-2024-0001")
        db = Mock()
        db.scalars.return_value = [existing]
        vulnerabilities = [
            {"cve": {"id": "CVE-2024-0001"}},
            {"cve": {"id": "CVE-2024-0002", "descriptions": [{"lang": "en", "value": "Example"}]}},
        ]
        inserted = persist_cves(db, str(uuid4()), technology, vulnerabilities)
        self.assertEqual(inserted, 1)
        db.add.assert_called_once()


if __name__ == "__main__":
    unittest.main()
