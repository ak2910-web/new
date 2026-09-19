#!/usr/bin/env python3
"""
Backfills backdated empty commits to draw a word into the GitHub
contribution graph.

Grid: 7 rows (Sun=row0 ... Sat=row6), each column = 1 week.
Each letter is a small bitmap; '1' = commit day, '0' = skip.

Run this from inside the repo (it commits with --allow-empty, it does
NOT push -- push separately so you can review first).
"""

import subprocess
from datetime import date, timedelta

# ---- config ----------------------------------------------------------
START_DATE = date(2026, 3, 29)  # must be a Sunday (row 0)
ON_COMMITS = 12                 # commits made on an "on" day, to stand
                                 # out against normal background activity
WORD = "RIYA"
GAP_COLS = 1                    # blank columns between letters

# 5x7 (rows top->bottom = Sun->Sat) bitmap fonts, 1 = filled
FONT = {
    "R": [
        "1111.",
        "1...1",
        "1...1",
        "1111.",
        "1.1..",
        "1..1.",
        "1...1",
    ],
    "I": [
        "111",
        ".1.",
        ".1.",
        ".1.",
        ".1.",
        ".1.",
        "111",
    ],
    "Y": [
        "1...1",
        "1...1",
        ".1.1.",
        "..1..",
        "..1..",
        "..1..",
        "..1..",
    ],
    "A": [
        ".11.",
        "1..1",
        "1..1",
        "1111",
        "1..1",
        "1..1",
        "1..1",
    ],
}


def build_columns(word):
    """Return list of 7-char strings, one per column, across whole word."""
    cols = []
    for i, letter in enumerate(word):
        rows = FONT[letter]
        width = len(rows[0])
        for c in range(width):
            cols.append("".join(rows[r][c] for r in range(7)))
        if i != len(word) - 1:
            for _ in range(GAP_COLS):
                cols.append("0000000")
    return cols


def run(cmd, env=None):
    subprocess.run(cmd, check=True, env=env)


def main():
    import os

    columns = build_columns(WORD)
    print(f"Word '{WORD}' -> {len(columns)} columns "
          f"({len(columns) * 7} days, ends "
          f"{START_DATE + timedelta(days=len(columns) * 7 - 1)})")

    made = 0
    for c, col in enumerate(columns):
        for r, on in enumerate(col):
            if on != "1":
                continue
            day = START_DATE + timedelta(days=c * 7 + r)
            for k in range(ON_COMMITS):
                ts = f"{day.isoformat()}T{9 + (k % 10):02d}:{(k * 7) % 60:02d}:00"
                env = os.environ.copy()
                env["GIT_AUTHOR_DATE"] = ts
                env["GIT_COMMITTER_DATE"] = ts
                run(
                    [
                        "git", "commit", "--allow-empty",
                        "-m", f"chore: activity {day.isoformat()}",
                    ],
                    env=env,
                )
                made += 1
    print(f"Created {made} backdated empty commits. "
          f"Review with `git log --oneline`, then `git push`.")


if __name__ == "__main__":
    main()
