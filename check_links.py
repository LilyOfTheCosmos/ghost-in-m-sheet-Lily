#!/usr/bin/env python3
"""
Passage link checker for Better Ghost Hunter (Twine/SugarCube).

Finds broken links: references to passage names that don't exist.
"""

import re
import sys
from pathlib import Path

# SugarCube built-in passage names - these are valid targets even without a definition
SUGARCUBE_BUILTINS = {
    "StoryAuthor", "StoryBanner", "StoryCaption", "StoryMenu", "StoryTitle",
    "StoryInit", "StoryData", "StoryScript", "StoryStylesheet",
    "PassageDone", "PassageFooter", "PassageHeader", "PassageReady",
}

# Regex to extract the passage name from a :: header line
PASSAGE_HEADER = re.compile(r"^::\s*(.+?)(?:\s*[\[{].*)?$")

# All link patterns that reference another passage:
#   [[Target]]
#   [[Text|Target]]  or  [[Text->Target]]  or  [[Text<-Target]]
#   <<link "text" "Target">>  or  <<link 'text' 'Target'>>
#   <<goto "Target">>  or  <<goto 'Target'>>
#   <<include "Target">>  or  <<include 'Target'>>
LINK_PATTERNS = [
    # [[Target]] — simple bracket link
    re.compile(r"\[\[([^\]|>]+?)\]\]"),
    # [[Text|Target]] — pipe syntax
    re.compile(r"\[\[[^\]]+?\|([^\]]+?)\]\]"),
    # [[Text->Target]] — arrow syntax
    re.compile(r"\[\[[^\]]+?->\s*([^\]]+?)\]\]"),
    # [[Target<-Text]] — reverse arrow syntax
    re.compile(r"\[\[([^\]<]+?)\s*<-[^\]]+?\]\]"),
    # <<link "..." "Target">> or <<link '...' 'Target'>>
    re.compile(r'<<link\s+["\'][^"\']*["\']\s+["\']([^"\']+)["\']'),
    # <<goto "Target">> or <<goto 'Target'>>
    re.compile(r"""<<goto\s+["']([^"']+)["']"""),
    # <<include "Target">> or <<include 'Target'>>
    re.compile(r"""<<include\s+["']([^"']+)["']"""),
    # Engine.play('Target') — JS navigation
    re.compile(r"""Engine\.play\s*\(\s*["']([^"']+)["']\s*\)"""),
]

def is_dynamic(target: str) -> bool:
    """Return True if the target is a runtime expression, not a literal passage name."""
    t = target.strip()
    # SugarCube functions like previous(), passage(), etc.
    if "(" in t or ")" in t:
        return True
    # Variable references
    if t.startswith("$") or t.startswith("_"):
        return True
    return False


def collect_passages(passages_dir: Path) -> dict[str, Path]:
    """Return a mapping of passage name -> file path for every passage defined."""
    passages: dict[str, Path] = {}
    for tw_file in sorted(passages_dir.rglob("*.tw")):
        for line in tw_file.read_text(encoding="utf-8", errors="replace").splitlines():
            m = PASSAGE_HEADER.match(line)
            if m:
                name = m.group(1).strip()
                passages[name] = tw_file
    return passages


def collect_links(passages_dir: Path) -> list[tuple[str, int, str]]:
    """Return a list of (file_path, line_number, target) for every link found."""
    links: list[tuple[str, int, str]] = []
    for tw_file in sorted(passages_dir.rglob("*.tw")):
        text = tw_file.read_text(encoding="utf-8", errors="replace")
        for lineno, line in enumerate(text.splitlines(), 1):
            # Skip comment lines
            stripped = line.strip()
            if stripped.startswith("/*") or stripped.startswith("//"):
                continue
            for pattern in LINK_PATTERNS:
                for m in pattern.finditer(line):
                    target = m.group(1).strip()
                    if not is_dynamic(target):
                        links.append((str(tw_file), lineno, target))
    return links


def main():
    repo_root = Path(__file__).parent
    passages_dir = repo_root / "passages"

    if not passages_dir.is_dir():
        print(f"ERROR: passages directory not found at {passages_dir}", file=sys.stderr)
        sys.exit(1)

    passages = collect_passages(passages_dir)
    all_known = set(passages.keys()) | SUGARCUBE_BUILTINS

    links = collect_links(passages_dir)

    broken: list[tuple[str, int, str]] = []
    for file_path, lineno, target in links:
        if target not in all_known:
            broken.append((file_path, lineno, target))

    # Deduplicate while preserving order
    seen: set[tuple[str, str]] = set()
    unique_broken: list[tuple[str, int, str]] = []
    for file_path, lineno, target in broken:
        key = (file_path, target)
        if key not in seen:
            seen.add(key)
            unique_broken.append((file_path, lineno, target))

    print(f"Passages found : {len(passages)}")
    print(f"Links checked  : {len(links)}")

    if not unique_broken:
        print("No broken links found.")
        sys.exit(0)

    print(f"\nBROKEN LINKS ({len(unique_broken)} unique targets):\n")
    # Group by missing target for readability
    by_target: dict[str, list[tuple[str, int]]] = {}
    for file_path, lineno, target in unique_broken:
        by_target.setdefault(target, []).append((file_path, lineno))

    for target in sorted(by_target):
        refs = by_target[target]
        print(f'  "{target}"  — referenced in:')
        for file_path, lineno in refs:
            # Show path relative to repo root for brevity
            try:
                rel = Path(file_path).relative_to(repo_root)
            except ValueError:
                rel = file_path
            print(f"      {rel}:{lineno}")

    sys.exit(1)


if __name__ == "__main__":
    main()
