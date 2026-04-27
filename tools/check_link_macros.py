#!/usr/bin/env python3
"""
Detects SugarCube wikilinks whose target portion contains unevaluated
macro syntax (e.g. ``<<= var>>``).

The reported failure mode:

    [[Ask <<= _cName>> ...|<<= _cName>>HuntEndAlone]]

renders the literal string ``<<= _cName>> HuntEndAlone`` to the player
because the wikilink target portion is parsed as a passage name, not as
a macro template. The canonical fix is the backtick expression syntax:

    [[Ask <<= _cName>> ...|`_cName + "HuntEndAlone"`]]

This script walks ``passages/`` and flags any wikilink whose target
contains an unevaluated ``<<...>>`` macro outside of backticks. It is
deliberately a stand-alone parser rather than a regex pass: a regex over
``[[...]]`` mis-handles ``]`` characters inside macro arguments (e.g.
``_args[1]``), which is exactly the kind of construct most likely to
appear next to a buggy macro target.
"""

import sys
from pathlib import Path


def parse_wikilinks(text):
    """Yield ``(offset, content)`` for every ``[[...]]`` wikilink in ``text``.

    Tracks ``<<...>>`` macro nesting so that ``]`` inside macro arguments
    (e.g. ``_args[1]``) does not prematurely terminate the wikilink.
    """
    n = len(text)
    i = 0
    while i < n - 1:
        if text[i] == '[' and text[i + 1] == '[':
            j = i + 2
            depth = 0
            found = False
            while j < n - 1:
                if text[j] == '<' and text[j + 1] == '<':
                    depth += 1
                    j += 2
                    continue
                if text[j] == '>' and text[j + 1] == '>':
                    if depth > 0:
                        depth -= 1
                    j += 2
                    continue
                if depth == 0 and text[j] == ']' and text[j + 1] == ']':
                    yield (i, text[i + 2:j])
                    i = j + 2
                    found = True
                    break
                j += 1
            if not found:
                i += 1
            continue
        i += 1


def split_wikilink_content(content):
    """Split ``[[..]]`` contents into ``(display_text, target)``.

    Returns ``(content, None)`` for the simple ``[[Target]]`` form. The
    splitter respects ``<<...>>`` macro nesting so a ``|`` inside a macro
    argument (e.g. ``<<= a | b>>``) is not treated as the link separator.
    """
    n = len(content)
    i = 0
    depth = 0
    while i < n:
        if i + 1 < n and content[i] == '<' and content[i + 1] == '<':
            depth += 1
            i += 2
            continue
        if i + 1 < n and content[i] == '>' and content[i + 1] == '>':
            if depth > 0:
                depth -= 1
            i += 2
            continue
        if depth == 0:
            if content[i] == '|':
                return content[:i], content[i + 1:]
            if i + 1 < n and content[i] == '-' and content[i + 1] == '>':
                return content[:i], content[i + 2:]
            if i + 1 < n and content[i] == '<' and content[i + 1] == '-':
                return content[i + 2:], content[:i]
        i += 1
    return content, None


def target_has_unevaluated_macro(target):
    """Return True if ``target`` contains ``<<...>>`` macro syntax that
    SugarCube will treat as literal characters.

    A target wrapped in backticks is a TwineScript expression — anything
    inside is fine. Only ``<<`` occurrences outside of backtick segments
    count as bugs.
    """
    if target is None:
        return False
    in_backtick = False
    i = 0
    n = len(target)
    while i < n:
        ch = target[i]
        if ch == '`':
            in_backtick = not in_backtick
            i += 1
            continue
        if not in_backtick and i + 1 < n and ch == '<' and target[i + 1] == '<':
            return True
        i += 1
    return False


def offset_to_lineno(text, offset):
    return text.count('\n', 0, offset) + 1


def main():
    repo_root = Path(__file__).resolve().parent.parent
    passages_dir = repo_root / "passages"
    if not passages_dir.is_dir():
        print(f"ERROR: passages directory not found at {passages_dir}", file=sys.stderr)
        sys.exit(1)

    bugs = []
    total_links = 0
    for tw_file in sorted(passages_dir.rglob("*.tw")):
        text = tw_file.read_text(encoding="utf-8", errors="replace")
        for offset, content in parse_wikilinks(text):
            total_links += 1
            display, target = split_wikilink_content(content)
            # [[Target]] form: display IS target.
            if target is None:
                target = display
            if target_has_unevaluated_macro(target):
                lineno = offset_to_lineno(text, offset)
                rel = tw_file.relative_to(repo_root)
                bugs.append((rel, lineno, target.strip()))

    print(f"Wikilinks scanned: {total_links}")

    if bugs:
        print(f"\nUNEVALUATED MACROS IN WIKILINK TARGETS ({len(bugs)}):\n")
        for rel, ln, target in bugs:
            print(f"  {rel}:{ln}  →  target = {target!r}")
        print(
            "\nSugarCube does NOT evaluate <<...>> macros inside [[Text|target]]\n"
            "wikilink targets — they are treated as literal characters in the\n"
            "passage name. Use the backtick expression syntax instead, e.g.\n"
            '  [[Display|`_name + "Suffix"`]]\n'
        )
        sys.exit(1)

    print("No unevaluated macros found in wikilink targets.")
    sys.exit(0)


if __name__ == "__main__":
    main()
