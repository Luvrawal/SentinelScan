import unittest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import Mock, patch

from app.phase3 import cookie_findings, dns_findings, kev_cves, mark_kev_findings


class Phase3Tests(unittest.TestCase):
    @patch("app.phase3._txt")
    def test_dns_checks_spf_dmarc_and_dkim(self, txt):
        txt.side_effect = lambda name: {
            "example.com": ["v=spf1 -all"],
            "_dmarc.example.com": ["v=DMARC1; p=none"],
            "default._domainkey.example.com": ["v=DKIM1; p=abc"],
        }.get(name, [])
        self.assertEqual(dns_findings("example.com"), [])

    @patch("app.phase3.httpx.get")
    def test_cookie_flags_are_reported(self, get):
        response = Mock()
        response.headers.get_list.return_value = ["session=abc; Path=/"]
        get.return_value = response
        findings = cookie_findings("https://example.com")
        self.assertEqual(findings[0]["owasp"], "A04")
        self.assertIn("secure", findings[0]["description"])

    def test_kev_cache_and_badge_marking(self):
        cache = SimpleNamespace(cve_ids=["CVE-2024-0001"], expires_at=datetime.now(timezone.utc) + timedelta(hours=1))
        db = Mock()
        db.get.return_value = cache
        self.assertEqual(kev_cves(db), {"CVE-2024-0001"})
        finding = SimpleNamespace(cve_id="CVE-2024-0001", kev_known_exploited=False)
        mark_kev_findings(db, [finding], {"CVE-2024-0001"})
        self.assertTrue(finding.kev_known_exploited)


if __name__ == "__main__":
    unittest.main()
