"""Release behavior against real temporary git histories, not the working book."""
import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("release_content", ROOT / "scripts/release_content.py")
release = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release)


class Release(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.write("content/VERSION", "1.0.0\n")
        self.write("content/CHANGELOG.md", "# Changelog\n\n## 1.0.0\n\n- Original edition.\n")
        self.write("content/chapters/one.md", "# Original chapter\n")
        self.git("init", "-q")
        self.git("add", ".")
        self.commit()
        self.base = self.git("rev-parse", "HEAD")

    def write(self, path, text):
        destination = self.root / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(text, encoding="utf-8")

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.root), *args], text=True, stderr=subprocess.PIPE).strip()

    def commit(self):
        self.git("-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "fixture")

    def content_change(self):
        self.write("content/chapters/one.md", "# Corrected chapter\n")
        self.write("content/VERSION", "1.0.1\n")
        self.write("content/CHANGELOG.md", "# Changelog\n\n## 1.0.1\n\n- Correction.\n\n## 1.0.0\n\n- Original edition.\n")

    def accept(self):
        self.write("content/reviews/fixture.md", "# Test-only review\n\nScope: fixture chapter.\n\nVerdict: ACCEPT\n")
        release.record_review(self.root, "content/reviews/fixture.md")

    def test_tooling_only_changes_need_no_edition_or_acceptance(self):
        self.write("scripts/tool.py", "print('tooling')\n")
        self.assertEqual(release.check(self.root, self.base)["status"], "PASS")

    def test_content_change_requires_version_bump(self):
        self.write("content/chapters/one.md", "A correction\n")
        with self.assertRaisesRegex(ValueError, "increase content/VERSION"):
            release.check(self.root, self.base)

    def test_bumped_content_requires_actual_report(self):
        self.content_change()
        with self.assertRaisesRegex(ValueError, "without editorial acceptance"):
            release.check(self.root, self.base)

    def test_reviewed_content_passes_before_and_after_commit(self):
        self.content_change()
        self.accept()
        self.assertEqual(release.check(self.root, self.base)["status"], "PASS")
        self.git("add", ".")
        self.commit()
        self.assertEqual(release.check(self.root)["status"], "PASS")

    def test_source_changes_invalidate_acceptance(self):
        self.content_change()
        self.accept()
        self.write("content/chapters/one.md", "Another correction\n")
        with self.assertRaisesRegex(ValueError, "stale"):
            release.check(self.root, self.base)

    def test_report_changes_invalidate_acceptance(self):
        self.content_change()
        self.accept()
        self.write("content/reviews/fixture.md", "Changed review\nVerdict: ACCEPT\n")
        with self.assertRaisesRegex(ValueError, "report changed"):
            release.check(self.root, self.base)

    def test_revise_cannot_be_recorded_as_accept(self):
        self.write("content/reviews/fixture.md", "Unresolved blocker\nVerdict: REVISE\n")
        with self.assertRaisesRegex(ValueError, "Verdict: ACCEPT"):
            release.record_review(self.root, "content/reviews/fixture.md")

    def test_tooling_only_version_bump_is_rejected(self):
        self.write("content/VERSION", "1.0.1\n")
        self.write("content/CHANGELOG.md", "## 1.0.1\n\n- Tooling only.\n")
        with self.assertRaisesRegex(ValueError, "must not bump"):
            release.check(self.root, self.base)

    def test_untracked_chapter_requires_review(self):
        self.write("content/chapters/new.md", "New chapter\n")
        with self.assertRaisesRegex(ValueError, "increase content/VERSION"):
            release.check(self.root, self.base)

    def test_missing_changelog_entry_is_rejected(self):
        self.write("content/CHANGELOG.md", "# Changelog\n")
        with self.assertRaisesRegex(ValueError, "nonempty entry"):
            release.check(self.root, self.base)

    def test_invalid_base_does_not_silently_skip_checks(self):
        with self.assertRaises(subprocess.CalledProcessError):
            release.check(self.root, "missing-ref")

    def test_existing_acceptance_cannot_be_removed(self):
        self.accept()
        self.git("add", ".")
        self.commit()
        base = self.git("rev-parse", "HEAD")
        (self.root / release.RECORD).unlink()
        with self.assertRaisesRegex(ValueError, "cannot be removed"):
            release.check(self.root, base)
