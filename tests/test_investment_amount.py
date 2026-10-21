"""Ved investor site: funding-amount content and navigation checks.

Run with: python -B -m unittest discover -s tests -v
No external network or services required.
"""
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import re
import unittest

SITE = Path(__file__).resolve().parents[1] / "index.html"


class SiteParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.anchors: list[str] = []
        self.ids: list[str] = []
        self.labels: list[str] = []
        self.text_nodes: list[str] = []
        self.mail_links: list[str] = []

    def handle_starttag(self, tag, attrs):
        props = dict(attrs)
        if props.get("id"):
            self.ids.append(props["id"])
        if tag == "a":
            href = props.get("href", "")
            self.anchors.append(href)
            if href.startswith("mailto:"):
                self.mail_links.append(href)
        if props.get("aria-labelledby"):
            self.labels.append(props["aria-labelledby"])

    def handle_data(self, data):
        self.text_nodes.append(data)


class VedInvestmentWebsiteTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = SITE.read_text(encoding="utf-8-sig")
        cls.doc = SiteParser()
        cls.doc.feed(cls.html)
        cls.visible = re.sub(r"\\s+", " ", " ".join(cls.doc.text_nodes))

    def test_correct_current_funding_request(self):
        self.assertIn("₹2 crore", self.visible)
        self.assertIn("INR 2,00,00,000", self.visible)
        self.assertIn("Current investment request", self.visible)

    def test_no_obsolete_one_point_four_crore_request(self):
        self.assertNotRegex(
            self.html,
            r"(?i)(?:₹|INR\s*)?\s*1\s*[.]\s*4\s*(?:crore|cr\b)"
        )
        self.assertNotRegex(self.html, r"(?i)1[,.]40[,.]00[,.]000")

    def test_amount_is_ask_not_misrepresented_as_received(self):
        self.assertIn("seeking investment", self.visible.lower())
        self.assertIn("not funds already raised", self.visible.lower())
        self.assertIn("private MVP development", self.visible)

    def test_accessible_funding_navigation(self):
        self.assertEqual(self.doc.ids.count("funding"), 1)
        self.assertEqual(self.doc.ids.count("funding-heading"), 1)
        self.assertGreaterEqual(self.doc.anchors.count("#funding"), 2)
        self.assertIn("funding-heading", self.doc.labels)

    def test_founder_contact_remains_working_link(self):
        self.assertTrue(any(
            a.startswith("mailto:") and "?" in a
            for a in self.doc.mail_links
        ))
        self.assertIn("#founder", self.doc.anchors)
        self.assertIn("#product", self.doc.anchors)
        self.assertIn("#technology", self.doc.anchors)
        self.assertIn("#stage", self.doc.anchors)

    def test_website_remains_static_and_unchanged_layout(self):
        self.assertIn("<main>", self.html)
        self.assertIn("<footer>", self.html)
        self.assertIn("class=\"hero-grid\"", self.html)
        self.assertIn("class=\"funding-panel\"", self.html)
        self.assertIn("Watch 30-sec demo", self.visible)
        self.assertNotIn("<script", self.html.lower())
        self.assertNotIn('target="_blank" href="mailto:', self.html)


if __name__ == "__main__":
    unittest.main()
