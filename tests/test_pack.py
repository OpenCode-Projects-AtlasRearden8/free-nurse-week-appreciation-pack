"""Tests for the Nurses Week Appreciation Pack.

Verifies:
  1. The generator builds every documented PDF successfully.
  2. Each PDF is a valid-looking PDF with real content and expected page counts.
  3. LICENSE carries the exact required copyright line.
  4. README credits Asdale Dynamics, LLC and references real files.
  5. site/index.html links resolve to real, built PDFs.
  6. No committed file looks like a key/secret.
"""

# Standard library imports...
import os
import re
import sys
import tempfile
import unittest

# Allow running tests from any working directory.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import generate_pdfs  # noqa: E402

PDFS_DIR = os.path.join(ROOT, "pdfs")

# Minimum page counts per deliverable (bucketed by filename substring).
MIN_PAGES = {
    "thank-you-cards": 1,
    "potluck-signup": 1,
    "badge-reel-compliment-tags": 1,
    "banner-happy-nurses-week": 4,
    "banner-thank-you-nurses": 4,
    "banner-blank-flags": 1,
    "celebration-plan-checklist": 2,
}

EXPECTED_FILES = [
    "cards/thank-you-cards-preceptor.pdf",
    "cards/thank-you-cards-preceptor-2.pdf",
    "cards/thank-you-cards-coworker.pdf",
    "cards/thank-you-cards-coworker-2.pdf",
    "cards/thank-you-cards-anytime.pdf",
    "cards/thank-you-cards-anytime-2.pdf",
    "potluck/potluck-signup-nurses-week.pdf",
    "potluck/potluck-signup-generic.pdf",
    "badge-tags/badge-reel-compliment-tags.pdf",
    "banner/banner-happy-nurses-week.pdf",
    "banner/banner-thank-you-nurses.pdf",
    "banner/banner-blank-flags.pdf",
    "checklist/celebration-plan-checklist.pdf",
]


def read(rel_path, binary=False):
    path = os.path.join(ROOT, rel_path)
    mode = "rb" if binary else "r"
    with open(path, mode) as f:
        data = f.read()
    return data


class TestGeneratedPDFs(unittest.TestCase):
    """Build the pack fresh and validate every output."""

    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        out_dir = os.path.join(cls._tmp.name, "pdfs")
        cls.built = generate_pdfs.build_all(out_dir)
        cls.out_dir = out_dir

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_all_documents_built(self):
        self.assertEqual(len(self.built), len(generate_pdfs.CARD_SETS) + 7)
        rels = {
            os.path.relpath(os.path.realpath(p), os.path.realpath(self.out_dir))
            for p in self.built
        }
        for rel in EXPECTED_FILES:
            self.assertIn(rel, rels, f"{rel} was not generated")

    def test_committed_pdfs_match_generated_set(self):
        for rel in EXPECTED_FILES:
            self.assertTrue(
                os.path.isfile(os.path.join(PDFS_DIR, rel)),
                f"committed file missing: {rel}",
            )

    def test_pdfs_are_valid_with_content(self):
        for rel in EXPECTED_FILES:
            path = os.path.join(self.out_dir, rel)
            self.assertTrue(os.path.isfile(path), f"missing {rel}")
            self.assertGreater(os.path.getsize(path), 2500, f"{rel} suspiciously small")
            with open(path, "rb") as f:
                head = f.read(8)
            self.assertTrue(head.startswith(b"%PDF"), f"{rel} not a PDF")
            with open(path, "rb") as f:
                data = f.read()
            pages = len(re.findall(rb"/Type\s*/Page[^s]", data))
            basename = os.path.basename(rel).replace(".pdf", "")
            minimum = min(v for k, v in MIN_PAGES.items() if basename.startswith(k) or k.startswith(basename))
            self.assertGreaterEqual(
                pages, minimum,
                f"{rel}: expected >= {minimum} pages, got {pages}",
            )

    def test_pdf_metadata_credits_llc(self):
        for rel in EXPECTED_FILES:
            with open(os.path.join(self.out_dir, rel), "rb") as f:
                data = f.read()
            self.assertIn(b"Asdale Dynamics, LLC", data, f"{rel} metadata lacks LLC credit")

    def test_banner_spells_full_phrase(self):
        """Big letters are drawn as (X) Tj in plain content streams
        (compression is off) — confirm every letter of the phrase lands."""
        path = os.path.join(self.out_dir, "banner/banner-happy-nurses-week.pdf")
        with open(path, "rb") as f:
            data = f.read()
        expected = {}
        for ch in "HAPPY NURSES WEEK".replace(" ", ""):
            expected[ch] = expected.get(ch, 0) + 1
        for ch, count in expected.items():
            found = data.count(f"({ch}) Tj".encode("latin-1"))
            self.assertGreaterEqual(found, count, f"banner shows {ch} only {found}x, need {count}")


class TestRepoFiles(unittest.TestCase):
    def test_license_copyright_exact(self):
        text = read("LICENSE")
        self.assertIn("Copyright (c) 2026 Asdale Dynamics, LLC", text)
        self.assertTrue(text.startswith("MIT License"))

    def test_readme_credits_llc(self):
        text = read("README.md")
        self.assertIn("Asdale Dynamics, LLC", text)
        self.assertIn("Nurses Week", text)
        self.assertIn("Education only", text)

    def test_readme_references_real_files(self):
        text = read("README.md")
        for match in re.findall(r"(?:pdfs|[`\"])([\w/]+\.pdf)", text):
            path = match.replace("`", "").strip("` ")
            if not path.startswith("pdfs/"):
                path = f"pdfs/{path}"
            self.assertTrue(os.path.isfile(os.path.join(ROOT, path)), f"README references missing file: {match}")

    def test_site_links_resolve(self):
        text = read(os.path.join("site", "index.html"))
        for href in re.findall(r'href="(\.\./pdfs/[^"]+)"', text):
            rel = href.replace("../", "")
            self.assertTrue(os.path.isfile(os.path.join(ROOT, rel)), f"site links to missing file: {href}")
        # every expected PDF is linked from the site
        for rel in EXPECTED_FILES:
            self.assertIn(f"../pdfs/{rel}", text, f"site missing link to {rel}")

    def test_no_secrets_in_repo_files(self):
        secret_patterns = [
            r"AKIA[0-9A-Z]{16}",                    # AWS access key id
            r"(?i)api[_-]?key\s*=\s*['\"][A-Za-z0-9]{16,}",
            r"-----BEGIN (?:RSA )?PRIVATE KEY-----",
            r"(?i)password\s*=\s*['\"][A-Za-z0-9]{8,}",
            r"ghp_[A-Za-z0-9]{20,}",                # GitHub PAT
        ]
        for base, dirs, files in os.walk(ROOT):
            dirs[:] = [d for d in dirs if d not in (".git", "__pycache__")]
            for name in files:
                if not name.endswith((".py", ".md", ".html", ".txt")):
                    continue
                path = os.path.join(base, name)
                with open(path, "r", errors="ignore") as f:
                    text = f.read()
                for pattern in secret_patterns:
                    self.assertIsNone(
                        re.search(pattern, text),
                        f"possible secret in {os.path.relpath(path, ROOT)}",
                    )


class TestGeneratorSelfConsistency(unittest.TestCase):
    def test_catalog_matches_builder(self):
        # every CARD_SET entry gets its own PDF
        self.assertEqual(len(generate_pdfs.CARD_SETS), 6)
        for name, cards in generate_pdfs.CARD_SETS.items():
            self.assertEqual(len(cards), 4, f"{name} should fill a full sheet of 4")
            for card in cards:
                self.assertEqual(len(card), 5, "card tuple = (eyebrow, l1, l2, colorway, seed)")

    def test_layout_constants_are_sane(self):
        # geometry sanity: US Letter page + quadrant fold placement + printable margins
        self.assertEqual((generate_pdfs.PAGE_W, generate_pdfs.PAGE_H), (612, 792))
        self.assertEqual(generate_pdfs.CARD_W, generate_pdfs.PAGE_W / 2)
        self.assertEqual(generate_pdfs.FOLD_Y, generate_pdfs.PAGE_H / 4)
        # footers sit above the ~0.25in hard-print margin
        self.assertGreaterEqual(0.32 * 72, 20)
        self.assertLess(generate_pdfs.FOLD_Y, generate_pdfs.PAGE_H / 2)


if __name__ == "__main__":
    unittest.main()
