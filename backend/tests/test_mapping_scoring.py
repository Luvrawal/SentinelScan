import unittest
from types import SimpleNamespace

from app.mapping import OWASP_CATEGORIES, owasp_category
from app.scoring import cvss_severity, sort_findings


class MappingAndScoringTests(unittest.TestCase):
    def test_all_owasp_categories_are_valid(self):
        self.assertEqual(OWASP_CATEGORIES, {f"A{index:02d}" for index in range(1, 11)})
        for tags in ([], ["unknown"], ["misconfig"], ["cve"], ["cookie"], ["exception"]):
            self.assertIn(owasp_category(tags), OWASP_CATEGORIES)

    def test_tag_mapping_uses_normalized_tags(self):
        self.assertEqual(owasp_category(["EXPOSURE"]), "A01")
        self.assertEqual(owasp_category(["headers"]), "A06")
        self.assertEqual(owasp_category(["cookie"]), "A04")
        self.assertEqual(owasp_category(["exception"]), "A10")

    def test_cvss_boundaries_are_exact(self):
        self.assertEqual(cvss_severity(10.0), "Critical")
        self.assertEqual(cvss_severity(9.0), "Critical")
        self.assertEqual(cvss_severity(8.9), "High")
        self.assertEqual(cvss_severity(7.0), "High")
        self.assertEqual(cvss_severity(6.9), "Medium")
        self.assertEqual(cvss_severity(4.0), "Medium")
        self.assertEqual(cvss_severity(3.9), "Low")
        self.assertEqual(cvss_severity(0.1), "Low")
        self.assertEqual(cvss_severity(None, "not-a-severity"), "Low")

    def test_sorting_prioritizes_severity_then_score(self):
        findings = [
            SimpleNamespace(title="medium", severity="Medium", cvss_score=4.0),
            SimpleNamespace(title="critical-low", severity="Critical", cvss_score=9.0),
            SimpleNamespace(title="critical-high", severity="Critical", cvss_score=9.8),
            SimpleNamespace(title="low", severity="Low", cvss_score=1.0),
            SimpleNamespace(title="high", severity="High", cvss_score=7.0),
        ]
        self.assertEqual(
            [finding.title for finding in sort_findings(findings)],
            ["critical-high", "critical-low", "high", "medium", "low"],
        )


if __name__ == "__main__":
    unittest.main()
