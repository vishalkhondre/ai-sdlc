"""Validate prose editions and bind an actual editorial report to its sources.

Tooling-only changes need no edition bump. Existing content predating this gate
is grandfathered until changed; new content changes require a fresh ACCEPT report.
This record establishes freshness, not the reviewer's identity or human approval.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD = "content/release-review.json"
SEMVER = re.compile(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)")


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True, stderr=subprocess.PIPE).strip()


def authored(path: str) -> bool:
    return (path.startswith("content/") and not path.startswith("content/reviews/")
            and path not in {RECORD, "content/VERSION", "content/CHANGELOG.md"}
            and "__pycache__" not in Path(path).parts and not path.endswith(".pyc"))


def source_files(root: Path) -> list[Path]:
    return sorted(p for p in (root / "content").rglob("*") if p.is_file()
                  and (authored(p.relative_to(root).as_posix())
                       or p.name in {"VERSION", "CHANGELOG.md"}))


def fingerprint(root: Path) -> str:
    digest = hashlib.sha256()
    for path in source_files(root):
        digest.update(path.relative_to(root).as_posix().encode() + b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def edition(value: str) -> tuple[int, int, int]:
    if not SEMVER.fullmatch(value):
        raise ValueError(f"Invalid content edition {value!r}; use MAJOR.MINOR.PATCH.")
    return tuple(map(int, value.split(".")))


def report_path(root: Path, value: str) -> Path:
    path = (root / value).resolve()
    if not path.is_relative_to((root / "content/reviews").resolve()) or path.suffix != ".md":
        raise ValueError("Review report must be a Markdown file under content/reviews/.")
    return path


def check_report(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    verdicts = re.findall(r"^Verdict: (ACCEPT|REVISE)\s*$", text, re.M)
    if verdicts != ["ACCEPT"]:
        raise ValueError("Review report must contain exactly one standalone Verdict: ACCEPT line.")


def record_review(root: Path, report: str) -> dict:
    path = report_path(root, report)
    check_report(path)
    data = {"verdict": "ACCEPT", "source_sha256": fingerprint(root),
            "report": path.relative_to(root).as_posix(),
            "report_sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    (root / RECORD).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return data


def check_review(root: Path) -> None:
    record = root / RECORD
    if not record.exists():
        raise ValueError("Content changed without editorial acceptance. Obtain a review, then run record-review.")
    data = json.loads(record.read_text(encoding="utf-8"))
    if data.get("verdict") != "ACCEPT" or data.get("source_sha256") != fingerprint(root):
        raise ValueError("Editorial acceptance is stale for these sources; request a fresh review.")
    path = report_path(root, data["report"])
    check_report(path)
    if data.get("report_sha256") != hashlib.sha256(path.read_bytes()).hexdigest():
        raise ValueError("Editorial report changed after acceptance; request a fresh review.")


def check(root: Path, base: str | None = None) -> dict:
    version = (root / "content/VERSION").read_text(encoding="utf-8").strip()
    current = edition(version)
    notes = (root / "content/CHANGELOG.md").read_text(encoding="utf-8")
    entry = re.search(rf"^## {re.escape(version)}(?:[ \t]+[^\n]*)?\n(.*?)(?=^## |\Z)", notes, re.M | re.S)
    if not entry or not entry.group(1).strip():
        raise ValueError(f"CHANGELOG.md needs a nonempty entry for {version}.")
    if base:
        base = git(root, "rev-parse", "--verify", f"{base}^{{commit}}")
    else:
        # Manual validation uses the preceding commit; an initial commit compares
        # to an empty tree and requires initial editorial acceptance.
        try:
            base = git(root, "rev-parse", "--verify", "HEAD^")
        except subprocess.CalledProcessError:
            base = subprocess.check_output(["git", "-C", str(root), "hash-object", "-t", "tree", "--stdin"], input="", text=True).strip()
    changed = set(git(root, "diff", "--name-only", base, "--", "content").splitlines())
    changed.update(git(root, "ls-files", "--others", "--exclude-standard", "--", "content").splitlines())
    content_changes = sorted(p for p in changed if authored(p))
    base_paths = git(root, "ls-tree", "-r", "--name-only", base).splitlines()
    old = git(root, "show", f"{base}:content/VERSION") if "content/VERSION" in base_paths else None
    if content_changes:
        if old is not None and current <= edition(old):
            raise ValueError("Reader-visible content changed: increase content/VERSION and update CHANGELOG.md.")
        check_review(root)
    elif old is not None and version != old:
        raise ValueError("Tooling/metadata-only changes must not bump the prose edition.")
    elif (root / RECORD).exists():
        check_review(root)
    elif RECORD in changed:
        raise ValueError("An existing editorial acceptance record cannot be removed.")
    return {"status": "PASS", "version": version, "comparison_base": base,
            "content_changes": content_changes, "source_sha256": fingerprint(root)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("check")
    validate.add_argument("--base", help="Exact pre-change commit (PR base or push-before SHA).")
    record = commands.add_parser("record-review")
    record.add_argument("--report", required=True)
    commands.add_parser("fingerprint")
    args = parser.parse_args()
    try:
        root = args.root.resolve()
        result = (check(root, args.base) if args.command == "check" else
                  record_review(root, args.report) if args.command == "record-review" else fingerprint(root))
        print(json.dumps(result, indent=2))
        return 0
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f"Release validation failed: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
