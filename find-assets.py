import collections
import os
import re
import pathlib
from typing import List, Tuple, Pattern, Union

def recursive_grep(
    pattern: Union[str, Pattern],
    root: str,
    encoding: str = "utf-8",
    errors: str = "ignore",
) -> List[Tuple[str, str]]:
    """
    Recursively search files under `root` for regex `pattern`.

    Returns:
        List of (file_path, matched_string)
    """
    if isinstance(pattern, str):
        regex = re.compile(pattern)
    else:
        regex = pattern

    matches: List[Tuple[str, str]] = []

    for dirpath, _, filenames in os.walk(root):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)

            try:
                with open(filepath, "r", encoding=encoding, errors=errors) as f:
                    lno = 0
                    for line in f:
                        for m in regex.finditer(line):
                            matches.append((filepath, m.group(0), lno))
                        lno += 1
            except (OSError, IOError):
                # Skip unreadable files (permissions, special files, etc.)
                continue

    return matches

def main():
    results = recursive_grep(r"assets/.+", "passages/")
    found_count = 0
    not_found_count = 0
    not_found_entries = collections.defaultdict(list)
    for tw, s, lno in results:
        #m = re.match(r'(assets\/[^\"\']+)[\"\']', s)
        m = re.search(r'(assets[\/\w\.\s\-\_\,]+)', s)
        if m:
            s = m.group(1)
        #else:
        #    m = re.search(r'(assets[\/\w\.]+)', s)
        #    if m:
        #        s = m.group(1)
        #        print(f"Inner {s}")
        #print(f"Outer {s}")
        img = pathlib.Path(s)
        if not img.is_file():
            #print(f"{img}:{lno}: {s} not found")
            not_found_count += 1
            not_found_entries[str(img)].append((tw, lno))
        else:
            found_count += 1
    #exit(0)
    for img, sources in not_found_entries.items():
        print(f"{img=}")
        for tw, lno in sources:
            print(f"tw={str(tw)}:{lno}")
        print()
    print(f"{not_found_count=}")
    print(f"{found_count=}")

main()

