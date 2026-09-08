import unittest

from app.technology import extract_technology


class TechnologyExtractionTests(unittest.TestCase):
    def test_extracts_product_version_and_category(self):
        item = {
            "info": {
                "name": "Nginx technology detection",
                "tags": ["tech", "server"],
                "metadata": {"product": "nginx", "version": "v1.24.0"},
            }
        }
        self.assertEqual(
            extract_technology(item),
            {"name": "Nginx", "version": "1.24.0", "category": "server", "source": "nuclei"},
        )

    def test_accepts_top_level_tags_and_version_in_name(self):
        item = {"tags": ["tech", "cms"], "info": {"name": "WordPress v6.4.2"}}
        self.assertEqual(
            extract_technology(item),
            {"name": "WordPress v6.4.2", "version": "6.4.2", "category": "CMS", "source": "nuclei"},
        )

    def test_ignores_non_technology_finding(self):
        self.assertIsNone(extract_technology({"info": {"name": "Exposed panel", "tags": ["exposure"]}}))

    def test_normalizes_common_aliases(self):
        item = {"info": {"name": "Apache HTTPD", "tags": ["tech", "server"], "metadata": {"version": "2.4"}}}
        result = extract_technology(item)
        self.assertEqual(result["name"], "Apache HTTP Server")
        self.assertEqual(result["version"], "2.4")


if __name__ == "__main__":
    unittest.main()