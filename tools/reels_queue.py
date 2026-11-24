#!/usr/bin/env python3
"""Validate and move reel links in Ideas/Draft/reels.md.

  python3 tools/reels_queue.py check            # drop new links already in B; list pending
  python3 tools/reels_queue.py done <url> <IDEA.md>   # move one link from A to B
  python3 tools/reels_queue.py discard <url> <reason> # move a link to C and delete its draft

Processing a pending link (reading the video, writing the draft) is manual.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "app"))

from ideas_core import reels  # noqa: E402

PATH = ROOT / "Ideas" / "Draft" / "reels.md"


def main(argv):
    if not argv or argv[0] not in ("check", "done", "discard"):
        print(__doc__.strip())
        return 2
    if argv[0] == "check":
        result = reels.run_check(PATH)
        for url in result["discarded_hit"]:
            print(f"DISCARDED (in C, draft deleted): {url}")
        for url in result["removed"]:
            print(f"REMOVED (already processed): {url}")
        for url in result["pending"]:
            print(f"PENDING: {url}")
        if not result["removed"] and not result["pending"] and not result["discarded_hit"]:
            print("NOTHING: section A is empty")
        return 0
    if argv[0] == "discard":
        if len(argv) != 3:
            print("usage: reels_queue.py discard <url> <reason>")
            return 2
        try:
            reels.run_discard(PATH, argv[1], argv[2])
        except ValueError as exc:
            print(f"ERROR: {exc}")
            return 1
        print(f"DISCARDED: {argv[1]} ({argv[2]})")
        return 0
    if len(argv) != 3:
        print("usage: reels_queue.py done <url> <IDEA.md>")
        return 2
    try:
        reels.run_mark_done(PATH, argv[1], argv[2])
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"DONE: {argv[1]} -> {argv[2]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
