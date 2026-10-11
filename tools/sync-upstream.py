#!/usr/bin/env python3
"""Sync upstream changes to sphinx.writers.text into rst2txt.

This script exports commits from Sphinx touching sphinx/writers/text.py and
tests/test_writers/test_writer_text.py since the initial split up to a given
tag, rewrites paths in the fast-export stream, grafts the first commit onto the
corresponding split commit in rst2txt, and imports the commits into a local
branch.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys

SPHINX_SPLIT_COMMIT = "2810f77ed"
RST2TXT_SPLIT_COMMIT = "df1b66dab7a287e20587f109ac3c91bb0c698d73"

PATH_MAP: dict[bytes, bytes] = {
    b"sphinx/writers/text.py": b"textwriter.py",
    b"tests/test_writers/test_writer_text.py": b"tests/test_writer_text.py",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import changes to sphinx.writers.text from Sphinx."
    )
    parser.add_argument(
        "tag",
        help="Sphinx tag to sync from (e.g. v8.2.0)",
    )
    parser.add_argument(
        "--sphinx-dir",
        required=True,
        help="Path to the Sphinx git repository",
    )
    return parser.parse_args()


def resolve_tag(sphinx_dir: str, tag: str) -> str:
    """Resolve tag name in Sphinx repo."""
    for candidate in (tag, f"v{tag}"):
        res = subprocess.run(
            [
                "git",
                "-C",
                sphinx_dir,
                "rev-parse",
                "--verify",
                f"refs/tags/{candidate}^{{commit}}",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if res.returncode == 0:
            return candidate
    return tag


def main() -> int:
    args = parse_args()

    sphinx_dir = os.path.abspath(args.sphinx_dir)
    if not os.path.isdir(sphinx_dir):
        print(
            f"Error: Sphinx directory does not exist: {sphinx_dir}",
            file=sys.stderr,
        )
        return 1

    tag = resolve_tag(sphinx_dir, args.tag)
    branch = f"sphinx-{tag}"
    target_branch = f"refs/heads/{branch}".encode()

    paths_to_export = [p.decode() for p in PATH_MAP]
    print(
        f"Exporting commits from Sphinx ({SPHINX_SPLIT_COMMIT}..{tag}) for "
        f"{', '.join(paths_to_export)}..."
    )
    export_cmd = [
        "git",
        "-C",
        sphinx_dir,
        "fast-export",
        "--tag-of-filtered-object=drop",
        f"{SPHINX_SPLIT_COMMIT}..refs/tags/{tag}",
        "--",
        *paths_to_export,
    ]
    try:
        res = subprocess.run(export_cmd, capture_output=True, check=True)
    except subprocess.CalledProcessError as exc:
        print(
            f"Error exporting from Sphinx: {exc.stderr.decode()}",
            file=sys.stderr,
        )
        return 1

    lines = res.stdout.splitlines(keepends=True)
    new_lines: list[bytes] = []
    i = 0
    first_commit = True

    while i < len(lines):
        line = lines[i]
        if line.startswith(b"commit "):
            new_lines.append(b"commit " + target_branch + b"\n")
            i += 1
            if first_commit:
                first_commit = False
                while not lines[i].startswith(b"data "):
                    new_lines.append(lines[i])
                    i += 1
                data_len = int(lines[i].split()[1])
                new_lines.append(lines[i])
                i += 1
                msg = b""
                while len(msg) < data_len:
                    msg += lines[i]
                    new_lines.append(lines[i])
                    i += 1
                # Graft the initial upstream commit to the split commit in
                # rst2txt
                new_lines.append(f"from {RST2TXT_SPLIT_COMMIT}\n".encode())
                continue
        elif line.startswith((b"M ", b"D ")):
            for old_path, new_path in PATH_MAP.items():
                if line.endswith(b" " + old_path + b"\n"):
                    line = line[: -len(old_path) - 1] + new_path + b"\n"
                    break
            new_lines.append(line)
            i += 1
        else:
            new_lines.append(line)
            i += 1

    print(f"Importing rewritten history into branch '{branch}'...")
    try:
        subprocess.run(
            ["git", "fast-import", "--force"],
            input=b"".join(new_lines),
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        print(f"Error importing history: {exc}", file=sys.stderr)
        return 1

    print(
        f"\nSuccessfully populated branch '{branch}'.\n\n"
        f"You can inspect the history with:\n"
        f"  git log --graph --oneline master {branch}\n\n"
        f"To merge the changes:\n"
        f"  git merge {branch}\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
